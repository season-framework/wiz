from season.core.component.base.workspace import Workspace as Base, App as AppBase
from season.core.component.base.workspace import localized
from season.core.builder.service import Build

import season
import os
import datetime
from werkzeug.routing import Map, Rule

class Route:
    def __init__(self, workspace):
        self.workspace = workspace
        self.wiz = workspace.wiz
        self.id  = None
    
    def list(self):
        fs = self.workspace.fs("src", "route")
        routes = fs.files()
        res = []
        for id in routes:
            route = self(id).data(code=False)
            if route is None:
                continue
            res.append(route['package'])
        res.sort(key=lambda x: x['id'])
        return res

    def build(self):
        url_map = []
        rows = self.list()
        routes = []
        for row in rows:
            obj = dict()
            obj['route'] = row['route']
            obj['id'] = row['id']
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

        fs = self.workspace.fs("cache")
        fs.write.pickle("urlmap", url_map)
        return url_map

    def match(self, uri):
        if len(uri) > 1 and uri[-1] == "/": uri = uri[:-1]

        fs = self.workspace.fs("cache")
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

    def is_instance(self):
        return self.id is not None

    def __call__(self, id):
        if id is None: return self
        id = id.lower()
        route = Route(self.workspace)
        route.id = id
        return route

    @localized
    def proceed(self):
        wiz = self.wiz
        app_id = self.id
        data = self.data()

        if data is None:
            return
        
        ctrl = None
        
        if 'controller' in data['package'] and len(data['package']['controller']) > 0:
            ctrl = data['package']['controller']
            ctrl = self.workspace.controller(ctrl)
            ctrl = ctrl()

        tag = wiz.mode()
        logger = wiz.logger(f"[{tag}/route/{app_id}]")
        dic = self.dic()

        name = self.fs().abspath('controller.py')
        season.util.os.compiler(data['controller'], name=name, logger=logger, controller=ctrl, dic=dic, wiz=wiz)

    @localized
    def fs(self, *args):
        return self.workspace.fs('src', 'route', self.id, *args)

    @localized
    def dic(self, lang=None):
        APP_ID = self.id
        wiz = self.wiz
        fs = self.fs("dic")

        if lang is None:
            lang = wiz.request.language()
            lang = lang.lower()
        
        data = fs.read.json(f'{lang}.json', None)
        if data is None:
            data = fs.read.json("default.json", dict())
        
        class Loader:
            def __init__(self, dicdata):
                self.dicdata = dicdata

            def __call__(self, key=None):
                dicdata = self.dicdata
                if key is None: 
                    return season.util.std.stdClass(dicdata)
                
                key = key.split(".")
                tmp = dicdata
                for k in key:
                    if k not in tmp:
                        return ""
                    tmp = tmp[k]
                return tmp

        return Loader(data)

    @localized
    def data(self, code=True):
        APP_ID = self.id
        wiz = self.wiz
        fs = self.fs()

        pkg = dict()
        pkg['package'] = fs.read.json('app.json', None)
        if pkg['package'] is None:
            return None

        pkg['package']['id'] = APP_ID
        
        def readfile(key, filename, default=""):
            try: 
                pkg[key] = fs.read(filename)
            except: 
                pkg[key] = default
            return pkg
        
        if code:
            pkg = readfile("controller", "controller.py")
            pkg['dic'] = dict()
            if fs.isdir("dic"):
                dics = fs.files("dic")
                for dic in dics:
                    try:
                        lang = os.path.splitext(dic)[0]
                        lang = lang.lower()
                        pkg['dic'][lang] = fs.read(os.path.join("dic", dic), '{}')
                    except:
                        pass

        return pkg

    @localized
    def update(self, data):
        required = ['package', 'dic', 'controller']
        for key in required:
            if key not in data: 
                raise Exception(f"'`{key}`' not defined")

        for key in data:
            if type(data[key]) == str:
                data[key] = data[key].replace('', '')

        data['package']['id'] = self.id

        if len(data['package']['id']) < 3:
            raise Exception(f"id length at least 3")
        
        allowed = "qwertyuiopasdfghjklzxcvbnm.1234567890"
        for c in data['package']['id']:
            if c not in allowed:
                raise Exception(f"only alphabet and number and . in package id")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 'created' not in data['package']:
            data['package']['created'] = timestamp

        fs = self.fs()
        fs.write.json("app.json", data['package'])
        fs.write("controller.py", data['controller'])
        
        if fs.isdir("dic"):
            fs.delete("dic")
        fs.makedirs("dic")
        dicdata = data['dic']
        for lang in dicdata:
            val = dicdata[lang]
            lang = lang.lower()
            fs.write(os.path.join("dic", lang + ".json"), val)

        self.build()

    @localized
    def delete(self):
        self.fs().delete()
        self.build()

class App(AppBase):
    def __init__(self, workspace):
        super().__init__(workspace)

    def __call__(self, app_id):
        if app_id is None: return self
        app_id = app_id.lower()
        app = App(self.workspace)
        app.id = app_id
        return app

    def list(self):
        fs = self.workspace.fs('src', 'app')
        apps = fs.files()
        res = []
        for app_id in apps:
            app = self(app_id).data(code=False)
            if app is None:
                continue
            res.append(app['package'])
        res.sort(key=lambda x: x['id'])
        return res

    @localized
    def fs(self, *args):
        return self.workspace.fs('src', 'app', self.id, *args)

    @localized
    def data(self, code=True):
        APP_ID = self.id
        wiz = self.wiz
        fs = self.fs()

        pkg = dict()
        pkg['package'] = fs.read.json('app.json', None)
        if pkg['package'] is None:
            return None

        pkg['package']['id'] = APP_ID
        
        viewtype = 'pug'
        if 'viewtype' in pkg['package']:
            viewtype = pkg['package']['viewtype']
        if viewtype not in ['pug', 'html']:
            viewtype = 'pug'

        def readfile(key, filename, default=""):
            try: 
                pkg[key] = fs.read(filename)
            except: 
                pkg[key] = default
            return pkg
        
        if code:
            pkg = readfile("api", "api.py")
            pkg = readfile("socketio", "socketio.py")
            pkg = readfile("view", f"view.{viewtype}")
            pkg = readfile("typescript", f"view.ts")
            pkg = readfile("scss", f"view.scss")

            pkg['dic'] = dict()
            if fs.isdir("dic"):
                dics = fs.files("dic")
                for dic in dics:
                    try:
                        lang = os.path.splitext(dic)[0]
                        lang = lang.lower()
                        pkg['dic'][lang] = fs.read(os.path.join("dic", dic), '{}')
                    except:
                        pass

        return pkg

    def before_update(self, data):
        required = ['package', 'dic', 'api', 'socketio', 'view', 'typescript', 'scss']
        for key in required:
            if key not in data: 
                raise Exception(f"'`{key}`' not defined")

        data['package']['id'] = self.id
        if len(data['package']['id']) < 3:
            raise Exception(f"id length at least 3")

        allowed = "qwertyuiopasdfghjklzxcvbnm.1234567890"
        for c in data['package']['id']:
            if c not in allowed:
                raise Exception(f"only alphabet and number and . in package id")

        return data

    def do_update(self, data):
        viewtype = 'pug'
        if 'viewtype' in data['package']:
            viewtype = data['package']['viewtype']
        if viewtype not in ['pug', 'html']:
            viewtype = 'pug'

        fs = self.fs()
        fs.write("api.py", data['api'])
        fs.write("socketio.py", data['socketio'])
        fs.write(f"view.{viewtype}", data['view'])
        fs.write("view.ts", data['typescript'])
        fs.write("view.scss", data['scss'])

class Workspace(Base):
    def __init__(self, wiz):
        super().__init__(wiz)
        buildClass = Build
        if wiz.server.config.build.Build is not None:
            buildClass = wiz.server.config.build.Build

        self.build = Build(self)
        self.app = App(self)
        self.route = Route(self)

    def path(self, *args):
        if self.wiz.server.is_bundle:
            return os.path.join(self.wiz.server.path.root, "project", *args)
        return self.wiz.branch.path(*args)
    
    def controller(self, namespace):
        wiz = self.wiz
        fs = self.fs("src", "controller")
        code = fs.read(f"{namespace}.py")
        logger = wiz.logger(f"[ctrl/{namespace}]")
        ctrl = season.util.os.compiler(code, name=fs.abspath(namespace + ".py"), logger=logger, wiz=wiz)
        return ctrl['Controller']
    
    def model(self, namespace):
        wiz = self.wiz
        fs = self.fs("src", "model")
        code = fs.read(f"{namespace}.py")
        logger = wiz.logger(f"[model/{namespace}]")
        model = season.util.os.compiler(code, name=fs.abspath(namespace + ".py"), logger=logger, wiz=wiz)
        return model['Model']