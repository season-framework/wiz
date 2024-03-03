import season
import os
import datetime
import copy
from werkzeug.routing import Map, Rule

class Model:
    def __init__(self, path=None):
        if path is None:
            path = wiz.project.fs().abspath()
        self.PATH_ROOT = path
        self.id  = None

    def rootfs(self, *args):
        return season.util.filesystem(os.path.join(self.PATH_ROOT, *args))

    def cache(self, key=None):
        cachens = 'route#' + wiz.project()
        cache = wiz.server.cache.get(cachens, dict())
        if key is None:
            return cache
        if key in cache:
            return cache[key]
        return None
    
    def list(self):
        fs = self.rootfs("bundle", "src", "route")
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

        cache = self.cache()
        cache['urlmap'] = url_map

        return url_map

    def match(self, uri):
        if len(uri) > 1 and uri[-1] == "/": uri = uri[:-1]

        _urlmap = self.cache('urlmap')
        if _urlmap is None:
            _urlmap = self.build()
        _urlmap = copy.deepcopy(_urlmap)

        urlmap = Map(_urlmap)
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
        route = Model(self.PATH_ROOT)
        route.id = id
        return route

    def proceed(self):
        app_id = self.id
        data = self.data()

        if data is None:
            return
        
        ctrl = None
        
        if 'controller' in data['package'] and len(data['package']['controller']) > 0:
            ctrl = data['package']['controller']
            ctrl = wiz.controller(ctrl)
            ctrl = ctrl()

        logger = wiz.logger(f"route/{app_id}")

        name = self.fs().abspath('controller.py')
        namespace = 'route.fn#' + name
        cache = self.cache()
        if namespace in cache:
            code = cache[namespace]
        else:
            code = data['controller']
            code = compile(code, name, 'exec')
            cache[namespace] = code
            
        season.util.compiler().build(code, name=name, logger=logger, controller=ctrl, wiz=wiz)

    def fs(self, *args):
        fs = self.rootfs('bundle', 'src', 'route', self.id, *args)
        return fs

    def data(self, code=True):
        APP_ID = self.id
        fs = self.fs()
        cache = self.cache()

        namespace = "route.code#" + APP_ID
        if code:
            if namespace in cache:
                return cache[namespace]

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
            cache[namespace] = pkg

        return pkg
