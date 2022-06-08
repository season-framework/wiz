import season
import datetime
import os
from werkzeug.routing import Map, Rule
from abc import *

class Route(metaclass=ABCMeta):
    def __init__(self, wiz):
        self.wiz = wiz
        self.branch = wiz.branch

    @abstractmethod
    def basepath(self):
        pass

    @abstractmethod
    def cachepath(self):
        pass
    
    def list(self):
        fs = season.util.os.FileSystem(self.basepath())
        routes = fs.files()
        res = []
        for id in routes:
            if fs.isfile(f"{id}/app.json"):
                pkg = self(id)
                res.append(pkg.data(code=False))
        res.sort(key=lambda x: x['package']['id'])
        return res
    
    def cachefs(self):
        path = self.cachepath()
        fs = season.util.os.FileSystem(path)
        return fs

    def clean(self):
        fs = self.cachefs()
        fs.delete()

    def build(self):
        url_map = []
        rows = self.list()
        routes = []
        for row in rows:
            obj = dict()
            obj['route'] = row['package']['route']
            obj['id'] = row['package']['id']
            routes.append(obj)
        
        for i in range(len(routes)):
            info = routes[i]
            route = info['route']
            if route is None: continue
            if len(route) == 0: continue

            endpoint = info["id"]

            if route == "/":
                url_map.append(Rule(route, endpoint=endpoint))
                continue

            if route[-1] == "/":
                url_map.append(Rule(route[:-1], endpoint=endpoint))
            elif route[-1] == ">":
                rpath = route
                while rpath[-1] == ">":
                    rpath = rpath.split("/")[:-1]
                    rpath = "/".join(rpath)
                    url_map.append(Rule(rpath, endpoint=endpoint))
                    if rpath[-1] != ">":
                        url_map.append(Rule(rpath + "/", endpoint=endpoint))
            url_map.append(Rule(route, endpoint=endpoint))

        fs = self.cachefs()
        fs.write.pickle("urlmap", url_map)
        return url_map

    def match(self, uri):
        if len(uri) > 1 and uri[-1] == "/": uri = uri[:-1]

        fs = self.cachefs()
        urlmap = fs.read.pickle("urlmap", None)
        if urlmap is None:
            urlmap = self.build()
        
        urlmap = Map(urlmap)
        urlmap = urlmap.bind("", "/")

        def matcher(url):
            try:
                endpoint, kwargs = urlmap.match(url, "GET")
                return endpoint, kwargs
            except:
                return None, {}
        
        id, segment = matcher(uri)
        return self(id), segment

    def load(self, id):
        if id is None: return None
        return self.Package(self, id)

    def __call__(self, id):
        return self.load(id)

    class Package:
        def __init__(self, manager, id):
            self.manager = manager
            self.fs = season.util.os.FileSystem(os.path.join(manager.basepath(), id))
            self.id = id

        def data(self, code=True):
            fs = self.fs
            pkg = dict()
            pkg["package"] = fs.read.json(f"app.json")
            def readfile(key, filename, default=""):
                try: pkg[key] = fs.read(filename)
                except: pkg[key] = default
                return pkg
            if code:
                pkg = readfile("controller", "controller.py")
            try:
                pkg['dic'] = fs.read.json("dic.json")
            except:
                pkg['dic'] = dict()
            return pkg

        def dic(self):
            class dicClass:
                def __init__(self, wiz, dicdata):
                    self.wiz = wiz
                    self.dicdata = dicdata

                def __call__(self, key=None):
                    dicdata = self.dicdata
                    language = self.wiz.request.language()
                    language = language.lower()
                    
                    if language in dicdata: dicdata = dicdata[language]
                    elif "default" in dicdata: dicdata = dicdata["default"]
                    
                    if key is None: return dicdata

                    key = key.split(".")
                    tmp = dicdata
                    for k in key:
                        if k not in tmp:
                            return ""
                        tmp = tmp[k]
                    return tmp

            fs = self.fs
            wiz = self.manager.wiz
            try:
                dicdata = fs.read.json("dic.json")
            except:
                dicdata = dict()
            return dicClass(wiz, dicdata)

        def proceed(self):
            wiz = self.manager.wiz
            request_uri = wiz.request.uri()
            app_id = self.id

            data = self.data()
            ctrl = None
            if 'controller' in data['package'] and len(data['package']['controller']) > 0:
                ctrl = data['package']['controller']
                ctrl = wiz.controller(ctrl, startup=True)

            tag = wiz.tag()
            logger = wiz.logger(f"[{tag}/route/{app_id}]", 94)
            dic = self.dic()

            name = os.path.join(wiz.basepath(), 'routes', app_id, 'controller.py')
            season.util.os.compiler(data['controller'], name=name, logger=logger, controller=ctrl, dic=dic, wiz=wiz)

        def update(self, data):
            # check structure
            required = ['package', 'dic', 'controller']
            for key in required:
                if key not in data: 
                    raise Exception(f"'`{key}`' not defined")

            required = ['id', 'route']
            for key in required:
                if key not in data['package']: 
                    raise Exception(f"'`package.{key}`' not defined")

            package = data['package']

            # check id format
            id = package['id']
            if len(id) < 3:
                raise Exception(f"id length at least 3")

            allowed = "qwertyuiopasdfghjklzxcvbnm.1234567890"
            for c in id:
                if c not in allowed:
                    raise Exception(f"only alphabet and number and . in package id")

            # update timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if 'created' not in package:
                package['created'] = timestamp
            package['updated'] = timestamp
            data['package'] = package

            # save file
            self.fs.write.json("app.json", data['package'])
            self.fs.write.json("dic.json", data['dic'])
            self.fs.write("controller.py", data['controller'])

            self.manager.build()
            return self

        def delete(self):
            self.fs.delete()