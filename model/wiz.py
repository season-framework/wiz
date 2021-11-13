import season

import base64
import lesscpy
import sass
import dukpy
from six import StringIO
import json
import os
import pypugjs
import datetime
from werkzeug.routing import Map, Rule

RELOADJS = """<script>
function wiz_devtools() {
    try {
        var socket = io("/wiz/devtools/reload/__ID__");
        socket._reload = false;
        socket.on("connect", function () {
            if (socket._reload) {
                location.reload();
            }
        });
        socket.on("reload", function (data) {
            if (data) {
                socket._reload = true;
                return;
            }
            location.reload()
        })
    } catch (e) {
    }
}
wiz_devtools();
</script>
"""


"""WIZ Process API
: this function used in wiz interfaces code editors and frameworks.

- log(*args)
- render(target_id, namespace, **kwargs)
- dic(key)
- controller(namespace)
- theme()
- resources(path)
"""

class Wiz:
    def __init__(self, wiz, **kwargs):
        self.__wiz__ = wiz
        self.__info__ = season.stdClass(kwargs)

        framework = wiz.framework
        self.request = framework.request
        self.response = framework.response
        self.config = framework.config

        # self.model = framework.model
        # self.lib = framework.lib
        
    def log(self, *args):
        tag = self.__info__.tag
        if tag is None: tag = "undefined"
        tag = "[wiz]" + tag
        log_color = self.__info__.log_color
        if log_color is None: log_color = "94"
        print(f"\033[93m{tag}\033[0m", *args)

    def dic(self, key):
        wiz = self.__wiz__
        mode = self.__info__.mode
        app_id = self.__info__.app_id

        if mode is None or app_id is None:
            return ""

        language = self.request.language()
        language = language.lower()
        
        # TODO: READ FROM CACHE
        if mode == 'route': 
            inst = wiz.cls.Route(wiz.framework)
        else: 
            inst = wiz.cls.App(wiz.framework)
        dic = inst.dic(app_id)

        if language in dic: dic = dic[language]
        if "default" in dic: dic = dic["default"]

        key = key.split(".")
        tmp = dic
        for k in key:
            if k not in tmp:
                return ""
            tmp = tmp[k]

        return tmp

    def controller(self, namespace):
        wiz = self.__wiz__
        fs = wiz.storage()
        fsns = fs.namespace
        fsns = os.path.join(fsns, "interfaces/controller")
        fs = fs.use(fsns)
        code = fs.read(namespace + ".py")
        wizinstance = wiz.instance(mode="interface.controller", app_id=self.__info__.app_id, tag=f"[interfaces][controller][{namespace}]", log_color="93")
        obj = {'__file__': 'season.wiz.interfaces.controller', '__name__': 'season.wiz.interfaces.controller', 'wiz': wizinstance, 'print': wizinstance.log}
        exec(compile(code, 'season.wiz.interfaces.controller', 'exec'), obj)
        return obj['Controller']

    def model(self, namespace):
        wiz = self.__wiz__
        fs = wiz.storage()
        fsns = fs.namespace
        fsns = os.path.join(fsns, "interfaces/model")
        fs = fs.use(fsns)
        code = fs.read(namespace + ".py")
        wizinstance = wiz.instance(mode="interface.model", app_id=self.__info__.app_id, tag=f"[interfaces][model][{namespace}]", log_color="93")
        obj = {'__file__': 'season.wiz.interfaces.model', '__name__': 'season.wiz.interfaces.controller', 'wiz': wizinstance, 'print': wizinstance.log}
        exec(compile(code, 'season.wiz.interfaces.model', 'exec'), obj)
        return obj['Model']
        
    def render(self, *args, **kwargs):
        if len(args) == 0: return ""

        target_id = args[0]

        # if args length is 1, namespace as target_id
        namespace = str(target_id)
        if len(args) > 1: namespace = str(args[1])

        # log trigger
        _prelogger = self.framework.log
        def _logger(*args):
            _prelogger(f"\033[94m[{namespace}]\033[0m", *args)
        self.framework.log = _logger

        # TODO: use cache

        # build source



"""Data Management APIs

- get(app_id, mode='app')
- rows(mode='app')
- update(info, mode='app')
- delete(app_id, mode='app')
"""
class DataManager:
    def __init__(self, wiz):
        self.__wiz__ = wiz
    
    def inst(self, mode):
        wiz = self.__wiz__
        if mode == 'route': inst = wiz.cls.Route(wiz.framework)
        else: inst = wiz.cls.App(wiz.framework)
        return inst

    def get(self, app_id, mode='app'):
        wiz = self.__wiz__
        branch = wiz.branch()
        inst = self.inst(mode)
        inst.checkout(branch)
        app = inst.get(app_id)
        return app

    def rows(self, mode='app'):
        wiz = self.__wiz__
        branch = wiz.branch()
        inst = self.inst(mode)
        inst.checkout(branch)
        apps = inst.rows()
        return apps

    def update(self, info, mode='app'):
        wiz = self.__wiz__
        branch = wiz.branch()
        inst = self.inst(mode)
        inst.checkout(branch)
        apps = inst.update(info)
        return apps

    def delete(self, app_id, mode='app'):
        wiz = self.__wiz__
        branch = wiz.branch()
        inst = self.inst(mode)
        inst.checkout(branch)
        inst.delete(app_id)


"""WIZ Cache API
: this class used in local only.

- get(key, default=None)
- set(key, value)
- flush()
"""
class CacheControl:
    def __init__(self, wiz):
        self.__wiz__ = wiz
        self.cache = wiz.framework.cache
        branch = wiz.branch()
        if 'wiz' not in self.cache:
            self.cache.wiz = season.stdClass()
        if branch not in self.cache.wiz:
            self.cache.wiz[branch] = season.stdClass()

    def fs(self):
        wiz = self.__wiz__
        branch = wiz.branch()
        return wiz.framework.model("wizfs", module="wiz").use(f"wiz/cache/{branch}")

    def get(self, key, default=None):
        wiz = self.__wiz__
        if wiz.is_dev():
            return None
        branch = wiz.branch()
        if branch in self.cache.wiz:
            if key in self.cache.wiz[branch]:
                return self.cache.wiz[branch][key]
        try:
            fs = self.fs()
            return fs.read_pickle(f"{key}.pkl")
        except:
            pass
        return default
        
    def set(self, key, value):
        wiz = self.__wiz__
        if wiz.is_dev():
            return False
        branch = wiz.branch()
        try:
            fs = self.fs()
            fs.write_pickle(f"{key}.pkl", value)
            self.cache.wiz[branch][key] = value
            return True
        except:
            pass
        return False
        
    def flush(self):
        wiz = self.__wiz__
        branch = wiz.branch()
        try:
            fs = self.fs()
            fs.remove(".")
        except:
            pass
        self.cache.wiz[branch] = season.stdClass()


""" WIZ Model used in framework level
"""
class Model:
    def __init__(self, framework):
        wizfs = framework.model("wizfs", module="wiz")
        
        # load package info
        try:
            opts = wizfs.use("modules/wiz").read_json("wiz-package.json")
        except:
            opts = {}
            
        # set variables
        self.package = season.stdClass(opts)
        self.framework = framework 

        # load config
        self.config = config = framework.config.load("wiz")

        # set storage
        wizsrc = config.get("src", "wiz")
        self.path = season.stdClass()
        self.path.root = wizsrc
        self.path.apps = os.path.join(wizsrc, "apps")
        self.path.cache = os.path.join(wizsrc, "cache")
        
        # set Env
        self.env = season.stdClass()
        self.env.DEVTOOLS = config.get("devtools", False)

        try:
            self.env.DEVMODE = framework.request.cookies("season-wiz-devmode", "false")
            if self.env.DEVMODE == "false": self.env.DEVMODE = False
            else: self.env.DEVMODE = True
        except:
            self.env.DEVMODE = False

        try: self.env.BRANCH = framework.request.cookies("season-wiz-branch", "master")
        except: self.env.BRANCH = "master"

        self.cls = season.stdClass()

        modulename = framework.modulename
        framework.modulename = "wiz"
        self.cls.Route = framework.lib.route.Route
        self.cls.App = framework.lib.app.App
        framework.modulename = modulename

        self.cache = CacheControl(self)
        self.data = DataManager(self)


    """WIZ Configuration API
    : configuration api used in wiz module.

    - set_env(name, value)  :
    - is_dev()              :
    - set_dev(DEVMODE)      :
    - checkout(branch)      :
    - themes()              :
    """

    def set_env(self, name, value=None):
        if value is None:
            if name in self.env:
                del self.env[name]
        else:
            self.env[name] = value
    
    def is_dev(self):
        return self.env.DEVMODE

    def set_dev(self, DEVMODE):
        """set development mode.
        :param DEVMODE: string variable true/false
        """
        self.framework.response.cookies.set("season-wiz-devmode", DEVMODE)
        if DEVMODE == "false": self.env.DEVMODE = False
        else: self.env.DEVMODE = True

    def branch(self):
        return self.env.BRANCH

    def checkout(self, branch):
        """checkout branch
        :param branch: string variable of branch name
        """
        self.framework.response.cookies.set("season-wiz-branch", branch)
        self.env.BRANCH = branch

        route_inst = self.cls.Route(self.framework)
        route_inst.checkout(branch)

        # route_inst = self.cls.App(self.framework)
        # route_inst.checkout(branch)

    def themes(self):
        framework = self.framework
        config = framework.config().load('wiz')
        BASEPATH = os.path.join(self.branchpath(), "themes")
        fs = framework.model("wizfs", module="wiz").use(BASEPATH)
        themes = fs.list()
        res = []
        for themename in themes:
            layoutpath = os.path.join(BASEPATH, themename, 'layout')
            fs = fs.use(layoutpath)
            layouts = fs.list()
            for layout in layouts:
                fs = fs.use(os.path.join(layoutpath, layout))
                if fs.isfile('layout.pug'):
                    res.append(f"{themename}/{layout}")
        return res

    def controllers(self):
        try:
            fs = self.storage()
            fsns = fs.namespace
            fsns = os.path.join(fsns, "interfaces/controller")
            fs = fs.use(fsns)
            rows = fs.files(recursive=True)
            ctrls = []
            for row in rows:
                if row[0] == "/": row = row[1:]
                name, ext = os.path.splitext(row)
                if ext == ".py":
                    ctrls.append(name)
            return ctrls
        except:
            pass
        return []

    def branchpath(self):
        branch = self.branch()
        return f"wiz/branch/{branch}"

    def storage(self):
        framework = self.framework
        branchpath = self.branchpath()
        return framework.model("wizfs", module="wiz").use(branchpath)

    # TODO
    def target_version(self):
        if self.env.DEVMODE:
            return "master"
        return "master"    


    """Process API
    : this function used in framework.
    
    - route()
    """

    def route(self):
        """select route wiz component and render view.
        this function used in season flask's filter.
        """

        cache = self.cache
        branch = self.branch()
        framework = self.framework

        # get request uri
        request_uri = framework.request.uri()

        # ignored for wiz admin interface.
        if request_uri.startswith("/wiz/") or request_uri == '/wiz':
            return

        routes = self.routes()
        app_id, segment = routes(request_uri)

        # if not found, proceed default policy of season flask
        if app_id is None:
            return

        # set segment for wiz component
        framework.request.segment = season.stdClass(segment)
        
        # build controller from route code
        route = cache.get(f"routes/{app_id}")

        if route is None:
            def addtabs(v, size=1):
                for i in range(size):
                    v =  "    " + "\n    ".join(v.split("\n"))
                return v

            inst = self.cls.Route(self.framework)
            route = inst.get(app_id)
            controller = route['controller']
            controller = addtabs(controller)
            controller = f"import season\ndef process(wiz):\n    kwargs = season.stdClass()\n    framework = wiz\n{controller}"
            route['controller'] = controller
            cache.set(f"routes/{app_id}", route)
            
        # setup logger
        wiz = self.instance(mode="route", app_id=app_id, tag=f"[route][{request_uri}]", log_color="93")
        
        controllerfn = {'__file__': 'season.Spawner', '__name__': 'season.Spawner', 'print': wiz.log}
        exec(compile(route["controller"], 'season.Spawner', 'exec'), controllerfn)

        if 'controller' in route['package']:
            ctrl = route['package']['controller']
            ctrl = wiz.controller(ctrl)
            if ctrl is not None:
                ctrl = ctrl()
                ctrl.__startup__(wiz)
        
        controllerfn['process'](wiz)


    """WIZ Private API
    : this function used in local only.
    
    - routes(): return all routes
    - instance(): return wiz api object
    """

    def routes(self):
        """load all routes in branch.
        this function used in local only.
        """

        cache = self.cache
        branch = self.branch()

        # load from cache, if `devmode` false
        routes = cache.get("routes")

        # if routes not in cache or `devmode` true, load routes            
        if routes is None:
            inst = self.cls.Route(self.framework)
            rows = inst.rows()
            routes = []
            for row in rows:
                obj = dict()
                obj['route'] = row['package']['route']
                obj['id'] = row['package']['id']
                routes.append(obj)
            cache.set("routes", routes)

        # generate url map
        url_map = []
        for i in range(len(routes)):
            info = routes[i]
            route = info['route']
            if route is None: continue
            if len(route) == 0: continue

            endpoint = info["id"]
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
        
        url_map = Map(url_map)
        url_map = url_map.bind("", "/")

        def matcher(url):
            try:
                endpoint, kwargs = url_map.match(url, "GET")
                return endpoint, kwargs
            except:
                return None, {}
        
        return matcher

    def instance(self, **kwargs):
        return Wiz(self, **kwargs)