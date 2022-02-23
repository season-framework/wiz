import season
import base64
import json
import os
import datetime
from werkzeug.routing import Map, Rule
import time
import markupsafe
import git
import io

def addtabs(v, size=1):
    for i in range(size):
        v =  "    " + "\n    ".join(v.split("\n"))
    return v

def spawner(code, namespace, logger, **kwargs):
    fn = {'__file__': namespace, '__name__': namespace, 'print': logger, 'season': season}
    for key in kwargs: fn[key] = kwargs[key]
    exec(compile(code, namespace, 'exec'), fn)
    return fn

class Storage(season.interfaces.wiz.model.fs.Model):
    def __init__(self, framework, plugin):
        super().__init__(framework)
        self.config.path = os.path.join(season.core.PATH.PROJECT, 'plugin', plugin)
        self.config.plugin = plugin

        if self.isdir(self.config.path) == False:
            raise Exception(f"plugin `{plugin}` not exists")

        self.config.path = os.path.join(self.config.path, "storage")
        self.namespace = ''

    def use(self, namespace):
        while namespace[0] == "/": namespace = namespace[1:]
        model = Storage(self.framework, self.config.plugin)
        model.namespace = namespace
        return model

class Plugin(season.stdClass):
    def __init__(self, framework, plugin_id):
        self.framework = framework
        self.PLUGIN_ID = plugin_id

        fs = framework.model("wizfs", module="wiz").use(f"wiz/plugin/{plugin_id}")

        self.__DATA__ = season.stdClass()
        self.__DATA__.info = season.stdClass(fs.read_json("plugin.wiz"))
        try: self.__DATA__.apps = fs.read_json("apps.wiz")
        except: self.__DATA__.apps = []
        try: self.__DATA__.route = season.stdClass(fs.read_json("route.wiz"))
        except: self.__DATA__.route = season.stdClass()

        self.__LAYOUTID__ = None
        self.__LAYOUTOPT__ = dict()
        
        def model(namespace):
            return framework.model(namespace, module="wiz")

        _redirect = framework.response.redirect
        def redirect(url):
            if url[0] == "/":
                return _redirect(url)
            
            base_route = self.info("route", "")
            try:
                if base_route[0] == "/": base_route = base_route[1:]
            except:
                pass
            url = os.path.join("/wiz/admin", base_route, url)
            return _redirect(url)
            
        self.flask = framework.flask
        self.flask_socketio = framework.flask_socketio
        self.socketio = framework.socketio
        self.lib = framework.lib
        self.model = model
        self.config = framework.config
        self.request = framework.request
        self.response = framework.response
        self.PATH = framework.core.PATH
        self.response.redirect = redirect
        self.__logger__ = self.logger("plugin")
        self.storage = Storage(framework, plugin_id)


    def logger(self, tag=None, log_color=94):
        class logger:
            def __init__(self, tag, log_color, wiz):
                self.tag = tag
                self.log_color = log_color
                self.wiz = wiz

            def log(self, *args):
                tag = self.tag
                log_color = self.log_color
                wiz = self.wiz
                
                if tag is None: tag = "undefined"
                tag = "[wiz]" + tag
                
                args = list(args)
                for i in range(len(args)): 
                    args[i] = str(args[i])
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                logdata = f"\033[{log_color}m[{timestamp}]{tag}\033[0m " + " ".join(args)
                print(logdata)

                wiz.socketio.emit("debug", logdata + "\n", namespace="/wiz", broadcast=True)
                
        return logger(tag, log_color, self).log

    def __dic__(self, app_id):
        class dic:
            def __init__(self, root, app_id):
                self.root = root
                self.app_id = app_id
            
            def dic(self, key=None):
                language = self.root.request.language()
                language = language.lower()
                
                dic = self.root.info("dic", dict())

                if language in dic: dic = dic[language]
                if "default" in dic: dic = dic["default"]

                if key is None:
                    return dic

                key = key.split(".")
                tmp = dic
                for k in key:
                    if k not in tmp:
                        return ""
                    tmp = tmp[k]

                return tmp

        dicinst = dic(self, app_id)
        return dicinst.dic

    def __compiler__(self, codelang, code, **kwargs):
        logger = self.logger(f"[compiler][{codelang}]")
        try:
            if code is None: return ""
            if len(code) == 0: return code
            fs = self.framework.model("wizfs", module="wiz").use(f"modules/wiz/compiler")
            if fs.isfile(f"{codelang}.py") == False:
                return code
            compiler = fs.read(f"{codelang}.py")
            compiler = spawner(compiler, "season.wiz.plugin.compiler", logger)
            return compiler['compile'](self, code, kwargs)
        except Exception as e:
            logger(e)
            raise e

    def info(self, key, default=None):
        if key in self.__DATA__.info:
            return self.__DATA__.info[key]
        return default

    def build(self):
        plugin_id = self.PLUGIN_ID
        enabled = self.info('enabled', False)
        framework = self.framework
                
        # build bundles (if another plugin use app_id, override by ordering level)
        fs = framework.model("wizfs", module="wiz").use(f"wiz/plugin/.cache/bundle")
        for app in self.__DATA__.apps:
            required = ['controller', 'api', 'html', 'js', 'css']
            for req in required: 
                if req not in app: 
                    app[req] = ""
            if 'dic' not in app: app['dic'] = dict()
            
            try: compile_opt_html = app['compile_html']
            except: compile_opt_html = 'on'
            try: compile_opt_js = app['compile_js']
            except: compile_opt_js = 'on'
            try: compile_opt_css = app['compile_css']
            except: compile_opt_css = 'on'

            app_id = app['id']
            fs.delete(app_id)

            render_id = "app_" + str(round(time.time())) + "_" + framework.lib.util.randomstring(8)
            
            bundle = dict()
            bundle['id'] = app_id
            bundle['plugin_id'] = plugin_id
            bundle['render_id'] = render_id

            controller = app['controller']
            controller = addtabs(controller)
            controller = f"import season\ndef process(**kwargs):\n{controller}\n    return kwargs"
            bundle['controller'] = controller

            bundle['api'] = app['api']

            compile_args = dict()
            compile_args['plugin_id'] = plugin_id
            compile_args['app_id'] = app_id
            compile_args['render_id'] = render_id
            
            bundle['html'] = self.__compiler__("pug", app['html'], **compile_args)
            bundle['js'] = app['js']

            if compile_opt_css == 'on':
                bundle['css'] = self.__compiler__("scss", app['css'], **compile_args)
            else:
                try:
                    bundle['css'] = self.__compiler__("scss", app['css'])
                except:
                    bundle['css'] = app['css']

            if compile_opt_html == 'on':
                bundle['html'] = self.__compiler__('html', bundle['html'], **compile_args)
            if compile_opt_js == 'on':
                bundle['js'] = self.__compiler__('javascript', app['js'], **compile_args)

            fs.write_pickle(app_id, bundle)
    
        # proceed builder
        route = self.__DATA__.route
        try:
            logger = self.logger(f"[plugin][builder][{plugin_id}]", 93)
            builder = route['builder']
            spawner(builder, 'season.wiz.plugin.builder', logger, framework=self)
        except:
            pass

        # build route, if route not set, not build
        base_route = self.info("route", "")
        try:
            if base_route[0] == "/": base_route = base_route[1:]
        except:
            pass

        if len(base_route) > 0:
            base_route = os.path.join("/wiz/admin", base_route, '<path:path>')

            fs = framework.model("wizfs", module="wiz").use(f"wiz/plugin/.cache")
            try:
                routes = fs.read_pickle("routes")
            except:
                routes = []

            replace_routes = []
            check_exists = False
            for r in routes:
                if r["plugin_id"] == plugin_id:
                    continue

                rlen = len(r['path'])
                if len(base_route) < rlen: rlen = len(base_route)
                if base_route[:rlen] == r['path'][:rlen]:
                    check_exists = True
                
                replace_routes.append(r)

            if check_exists == False:
                replace_routes.append({"path": base_route, "plugin_id": plugin_id})

            fs.write_pickle("routes", replace_routes)
        
        
    def nav(self, id, title, url, pattern):
        fs = self.framework.model("wizfs", module="wiz").use(f"wiz/plugin/.cache")
        try:
            nav = fs.read_pickle("nav")
        except:
            nav = []
        navids = [x['id'] for x in nav]
        if id not in navids:
            nav.append({"id": id, "title": title, "url": url, "pattern": pattern})
            fs.write_pickle("nav", nav)
        
    def subnav(self, parent, id, title, url, pattern):
        fs = self.framework.model("wizfs", module="wiz").use(f"wiz/plugin/.cache")
        try: subnav = fs.read_pickle("subnav")
        except: subnav = dict()

        if parent not in subnav:
            subnav[parent] = []
        
        navids = [x['id'] for x in subnav[parent]]
        if id not in navids:
            subnav[parent].append({"id": id, "title": title, "url": url, "pattern": pattern})
            fs.write_pickle("subnav", subnav)
    
    def layout(self, *args, **kwargs):
        if len(args) > 0:
            layout_id = args[0]
            fs = self.framework.model("wizfs", module="wiz").use(f"wiz/plugin/.cache/bundle")
            if fs.isfile(layout_id) == False:
                self.__LAYOUTID__ = None
                self.__LAYOUTOPT__ = None
                return False
            self.__LAYOUTID__ = layout_id
            self.__LAYOUTOPT__ = kwargs
        else:
            self.__LAYOUTID__ = None
            self.__LAYOUTOPT__ = None
        return True
    
    def match(self, route):
        if route[0] == "/": route = route[1:]
        base_route = self.info("route", "")
        if base_route[0] == "/": base_route = base_route[1:]
        route = os.path.join("/wiz/admin", base_route, route)

        endpoint = "exist"

        url_map = []
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
                
        request_uri = self.request.uri()
        endpoint, segment = matcher(request_uri)
        if endpoint is None:
            return None
        segment = season.stdClass(segment)
        return segment

    def render(self, *args, **kwargs):
        if len(args) == 0:
            return self

        framework = self.framework

        app_id = None
        route = None

        if len(args) == 1:
            app_id = args[0]
        else:
            route = args[0]
            app_id = args[1]
                    
        if route is None:
            view = self.view(app_id, **kwargs)
            if self.__LAYOUTID__ is not None:
                view = self.view(self.__LAYOUTID__, view=view, **self.__LAYOUTOPT__)
            framework.response.send(view, "text/html")

        if route[0] == "/": route = route[1:]
        base_route = self.info("route", "")
        if base_route[0] == "/": base_route = base_route[1:]
        route = os.path.join("/wiz/admin", base_route, route)
        
        url_map = []
        if route[-1] == "/":
            url_map.append(Rule(route[:-1], endpoint=app_id))
        elif route[-1] == ">":
            rpath = route
            while rpath[-1] == ">":
                rpath = rpath.split("/")[:-1]
                rpath = "/".join(rpath)
                url_map.append(Rule(rpath, endpoint=app_id))
                if rpath[-1] != ">":
                    url_map.append(Rule(rpath + "/", endpoint=app_id))
        url_map.append(Rule(route, endpoint=app_id))
        url_map = Map(url_map)
        url_map = url_map.bind("", "/")

        def matcher(url):
            try:
                endpoint, kwargs = url_map.match(url, "GET")
                return endpoint, kwargs
            except:
                return None, {}
                
        request_uri = self.request.uri()
        app_id, segment = matcher(request_uri)

        if app_id is None:
            return self

        self.request.segment = season.stdClass(segment)

        view = self.view(app_id, **kwargs)
        if self.__LAYOUTID__ is not None:
            view = self.view(self.__LAYOUTID__, view=view, **self.__LAYOUTOPT__)

        framework.response.send(view, "text/html")

    def view(self, app_id, **kwargs):
        framework = self.framework
        fs = self.framework.model("wizfs", module="wiz").use(f"wiz/plugin/.cache/bundle")
        if fs.isfile(app_id) == False:
            return ""

        bundle = fs.read_pickle(app_id)
        
        logger = self.logger(f"[plugin][bundle][{app_id}]", 93)
        dic = self.__dic__(app_id)
        controllerfn = spawner(bundle['controller'], 'season.plugin.bundle', logger, framework=self, dic=dic)
        kwargs = controllerfn['process'](**kwargs)
        kwargs['query'] = framework.request.query()

        dicstr = dic()
        dicstr = json.dumps(dicstr, default=season.json_default)
        dicstr = dicstr.encode('ascii')
        dicstr = base64.b64encode(dicstr)
        dicstr = dicstr.decode('ascii')

        kwargsstr = json.dumps(kwargs, default=season.json_default)
        kwargsstr = kwargsstr.encode('ascii')
        kwargsstr = base64.b64encode(kwargsstr)
        kwargsstr = kwargsstr.decode('ascii')

        kwargs['plugin'] = self

        view = bundle['html']
        js = bundle['js']
        css = bundle['css']
        
        compile_opt = self.info('compile', "controller")
        if compile_opt == 'controller':
            view = f'{view}<script type="text/javascript">{js}</script><style>{css}</style>'

        view = framework.response.template_from_string(view, framework=self, dicstr=dicstr, kwargs=kwargsstr, dic=dic, **kwargs)
        return markupsafe.Markup(view)

    def route(self):
        plugin_id = self.PLUGIN_ID
        route = self.__DATA__.route
        route_script = route['route']
        route_script = addtabs(route_script)
        route_script = f"import season\ndef process(framework):\n{route_script}"

        controller = season.interfaces.wiz.ctrl.admin.view()
        controller.__startup__(self.framework)

        logger = self.logger(f"[plugin][route][{plugin_id}]", 93)
        controllerfn = spawner(route_script, 'season.wiz.plugin.route', logger)
        controllerfn['process'](self)

    def api(self, bundle_id, fnname):
        framework = self.framework
        fs = self.framework.model("wizfs", module="wiz").use(f"wiz/plugin/.cache/bundle")
        if fs.isfile(bundle_id) == False:
            framework.response.status(404)

        bundle = fs.read_pickle(bundle_id)
        api = bundle['api']

        dic = self.__dic__(bundle_id)
        logger = self.logger(f"[plugin][api][{bundle_id}]", 93)
        
        apifn = spawner(api, 'season.wiz.plugin.api', logger, dic=dic, framework=self)
        
        if fnname not in apifn:
            framework.response.status(404)
        
        if '__startup__' in apifn: 
            apifn['__startup__'](self)
        apifn[fnname](self)

    def plugin(self, plugin_id):
        return Plugin(self.framework, plugin_id)

class Model:
    def __init__(self, framework):
        self.framework = framework
        self.fs = framework.model("wizfs", module="wiz").use("wiz/plugin")

    def list(self):
        fs = self.fs
        plugins = fs.files()
        res = []
        for plugin_id in plugins:
            try:
                plugin_file = os.path.join(plugin_id, "plugin.wiz")
                if fs.isfile(plugin_file):
                    plugin_info = fs.read_json(plugin_file)
                    plugin_info['id'] = plugin_id
                    res.append(plugin_info)
            except:
                pass
        return res

    def get(self, plugin_id):
        fs = self.fs
        info_file = os.path.join(plugin_id, "plugin.wiz")
        route_file = os.path.join(plugin_id, "route.wiz")
        apps_file = os.path.join(plugin_id, "apps.wiz")

        res = dict()
        try:
            res['info'] = fs.read_json(info_file)
            res['info']['id'] = plugin_id
        except: 
            return None

        try:
            res['route'] = fs.read_json(route_file)
        except: 
            res['route'] = dict()

        try:
            res['apps'] = fs.read_json(apps_file)
        except: 
            res['apps'] = []

        return res

    def create(self, plugin_id, name):
        if len(plugin_id) < 4:
            raise Exception(f"at least 4 char for Plugin ID")

        allowed = "qwertyuiopasdfghjklzxcvbnm.1234567890"
        for ns in plugin_id:
            if ns not in allowed:
                raise Exception(f"only alphabet and number and . in Plugin ID")

        fs = self.fs
        info_file = os.path.join(plugin_id, "plugin.wiz")
        route_file = os.path.join(plugin_id, "route.wiz")
        apps_file = os.path.join(plugin_id, "apps.wiz")

        if fs.isfile(info_file):
            raise Exception(f"Already exist plugin")

        info = dict()
        info["id"] = plugin_id
        info["name"] = name

        fs.write_json(info_file, info)

    def update(self, plugin_id, info, apps, route):
        fs = self.fs
        info_file = os.path.join(plugin_id, "plugin.wiz")
        route_file = os.path.join(plugin_id, "route.wiz")
        apps_file = os.path.join(plugin_id, "apps.wiz")

        if fs.isfile(info_file) == False:
            return False

        fs.write(info_file, info)
        fs.write(apps_file, apps)
        fs.write(route_file, route)

        self.instance(plugin_id).build()

        return True

    def delete(self, plugin_id):
        if len(plugin_id) == 0:
            raise Exception("Plugin ID not defined")
        fs = self.fs
        fs.delete(plugin_id)

    def build(self):
        fs = self.fs
        plugins = self.list()

        fs.delete(".cache")
        fs.makedirs(".cache")
        
        for plugin in plugins:
            plugin_id = plugin['id']
            plugin = self.instance(plugin_id)
            plugin.build()

    def route(self):
        fs = self.fs
        if fs.isdir(".cache") == False:
            self.build()

        framework = self.framework
        request_uri = framework.request.uri()        
        routes = self.routes()
        plugin_id, segment = routes(request_uri)
        if plugin_id is None:
            return

        orgseg = framework.request.segment
        framework.request.segment = season.stdClass(segment)
        plugin = self.instance(plugin_id)
        plugin.route()
        framework.request.segment = orgseg

    def routes(self):
        framework = self.framework
        fs = framework.model("wizfs", module="wiz").use(f"wiz/plugin/.cache")
        try:
            routes = fs.read_pickle("routes")
        except:
            routes = []

        url_map = []
        for i in range(len(routes)):
            info = routes[i]
            route = info['path']
            if route is None: continue
            if len(route) == 0: continue

            endpoint = info["plugin_id"]
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

    def instance(self, name):
        return Plugin(self.framework, name)