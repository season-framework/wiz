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
        
class Model(season.interfaces.wiz.model.sql.Model):
    def __init__(self, framework):
        super().__init__(framework)
        try:
            fs = framework.model("wizfs", module="wiz").use("modules/wiz")
            opts = fs.read_json("wiz-package.json")
        except:
            opts = {}
        self.package = season.stdClass(opts)
        self.framework = framework 
        self.cache = framework.cache

        if 'wiz' not in self.cache:
            _cache = None
            try:
                fs = self.framework.model("wizfs", module="wiz").use(".")
                _cache = fs.read_pickle("wiz.cache") 
            except:
                pass

            if _cache is None:
                self.cache.wiz = dict()
                self.cache.wiz['dev'] = dict()
                self.cache.wiz['prod'] = dict()
                self.cache.wiz['dev_theme'] = dict()
                self.cache.wiz['prod_theme'] = dict()
            else:
                self.cache.wiz = _cache
        
        config = framework.config.load("wiz")
        try:
            self.DEVMODE = framework.request.cookies("season-wiz-devmode", "false")
            if self.DEVMODE == "false": self.DEVMODE = False
            else: self.DEVMODE = True
        except:
            self.DEVMODE = False
        self.updateview = False
        self.wizconfig = config
        self.DEVTOOLS = config.get("devtools", False)

        if 'wiz_deploy_version' not in self.cache:
            versions = self.rows(groupby="version", orderby="`version` DESC", fields="version,count(*) AS cnt")
            for i in range(len(versions)):
                if versions[i]['cnt'] <= 1: continue
                if versions[i]['version'] == 'master': continue
                self.cache.wiz_deploy_version = versions[i]['version']
                break
            
    def deploy_version(self, version=None):
        if version is None:
            if 'wiz_deploy_version' not in self.cache:
                return 'master'
            return self.cache.wiz_deploy_version
        else:
            self.cache.wiz_deploy_version = version

    def flush(self):
        self.cache.wiz = dict()
        self.cache.wiz['dev'] = dict()
        self.cache.wiz['prod'] = dict()
        self.cache.wiz['dev_theme'] = dict()
        self.cache.wiz['prod_theme'] = dict()
        
        versions = self.rows(groupby="version", orderby="`version` DESC", fields="version,count(*) AS cnt")
        if 'wiz_deploy_version' not in self.cache:
            versions = self.rows(groupby="version", orderby="`version` DESC", fields="version,count(*) AS cnt")
            for i in range(len(versions)):
                if versions[i]['cnt'] <= 1: continue
                if versions[i]['version'] == 'master': continue
                self.cache.wiz_deploy_version = versions[i]['version']
                break

    def build(self):
        """build all interfaces.
        """

        # find all views
        rows = self.rows(fields="id,namespace", groupby="id")

        # get mode
        is_dev = self.is_dev()
        if is_dev: is_dev = "true"
        else: is_dev = "false"
        self.set_dev("false")

        # not used cache
        self.set_update_view(True)

        # iter all views for build
        for row in rows:
            try:
                namespace = row['namespace']
                self.render(namespace)
            except:
                pass

        # restore mode
        self.set_dev(is_dev)

        fs = self.framework.model("wizfs", module="wiz").use(".")
        fs.write_pickle("wiz.cache", self.cache.wiz)
        return True

    def set_update_view(self, updateview):
        """do not use cache for rendering.
        :param updateview: boolean true/false
        """
        self.updateview = updateview
    
    def is_dev(self):
        return self.DEVMODE

    def set_dev(self, DEVMODE):
        """set development mode.
        :param DEVMODE: string variable true/false
        """
        self.framework.response.cookies.set("season-wiz-devmode", DEVMODE)
        if DEVMODE == "false": self.DEVMODE = False
        else: DEVMODE = True

    def json_default(self, value):
        if isinstance(value, datetime.date): 
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return ""

    def get(self, **kwargs):
        if 'version' not in kwargs:
            if self.DEVMODE:
                kwargs['version'] = 'master'
                data = super().get(**kwargs)
            else:
                _version = self.deploy_version()
                if _version == 'master':
                    kwargs['version'] = {"op": "!=", "value": "master"}
                    data = super().get(**kwargs, orderby="`version` DESC")
                else:
                    kwargs['version'] = _version
                    data = super().get(**kwargs, orderby="`version` DESC")

                if data is None: 
                    kwargs['version'] = 'master'
                    data = super().get(**kwargs)
        else:
            data = super().get(**kwargs)

        if data is None: 
            return None

        try:
            data['properties'] = json.loads(data['properties'])
        except:
            data['properties'] = {"html": "pug", "css": "less", "js": "javascript"}

        return data

    def upsert_notbuild(self, values, **format):
        """Season Flask's default upsert function
        """
        res = super().upsert(values, **format)
        return res

    def upsert(self, values, **format):
        """Customized upsert function.
        upsert wiz component code and refresh cache
        """
        res = super().upsert(values, **format)

        # set not used cache mode
        self.set_update_view(True)

        # clear development cache
        self.cache.wiz['dev'] = season.stdClass()

        # build view and routes
        try:
            if 'route' not in values or len(values['route']) == 0:
                try:
                    self.render(values['id'])
                except:
                    pass
            else:
                try:
                    self.routes()
                except: 
                    pass
                
                try:
                    self.route()
                except:
                    pass

                self.framework.request.segment = season.stdClass()
                try:
                    self.render(values['id'])
                except:
                    pass
        except:
            pass

        return res

    def route(self):
        """select route wiz component and render view.
        this function used in season flask's filter.
        """
        framework = self.framework

        # get request uri
        requri = framework.request.uri()

        # ignored for wiz admin interface.
        if requri.startswith("/wiz/") or requri == '/wiz':
            return

        # find route view
        app_id = None
        theme = None
        routes = self.routes()
        app_id, theme, segment = routes(requri)

        # if not found, proceed default policy of season flask
        if app_id is None:
            return

        # set segment for wiz component
        framework.request.segment = season.stdClass(segment)

        # build & render view
        view = self.render(app_id)

        # find theme
        if theme is not None:
            theme = theme.split("/")
        else:
            theme = []

        if len(theme) != 2:
            theme = framework.config().load('wiz').get("theme_default", None)
            if theme is None:
                raise Exception("Theme Not Found")
            theme = theme.split("/")
            
        view = self.__theme__(theme[0], theme[1], view)
        framework.response.send(view, "text/html")

    # find routes
    def routes(self):
        """load route from wiz database. This function used only in this instance.
        """
        if self.DEVMODE:
            if 'routes' in self.cache.wiz['dev'] and self.updateview==False:
                return self.cache.wiz['dev']['routes']
        else:
            if 'routes' in self.cache.wiz['prod'] and self.updateview==False:
                return self.cache.wiz['prod']['routes']
        
        if self.DEVMODE:
            routes = self.select(version="master", fields="id,route,theme", orderby="`updated` DESC")
        else:
            routes = self.select(version=self.deploy_version(), fields="id,route,theme", orderby="`updated` DESC")

        url_map = []
        for i in range(len(routes)):
            info = routes[i]
            route = info['route']
            if route is None: continue
            if len(route) == 0: continue
            if route[-1] == "/":
                url_map.append(Rule(route[:-1], endpoint=info['id'] + ":" + info['theme']))
            elif route[-1] == ">":
                rpath = route
                while rpath[-1] == ">":
                    rpath = rpath.split("/")[:-1]
                    rpath = "/".join(rpath)
                    url_map.append(Rule(rpath, endpoint=info['id'] + ":" + info['theme']))
                    if rpath[-1] != ">":
                        url_map.append(Rule(rpath + "/", endpoint=info['id'] + ":" + info['theme']))
            
            url_map.append(Rule(route, endpoint=info['id'] + ":" + info['theme']))

        url_map = Map(url_map)
        url_map = url_map.bind("", "/")
        
        def matcher(url):
            try:
                endpoint, kwargs = url_map.match(url, "GET")
                endpoint = endpoint.split(":")
                return endpoint[0], endpoint[1], kwargs
            except:
                return None, None, {}

        if self.DEVMODE:
            self.cache.wiz['dev']['routes'] = matcher
            return self.cache.wiz['dev']['routes']
        else:
            self.cache.wiz['prod']['routes'] = matcher
            return self.cache.wiz['prod']['routes']
    
    def themes(self):
        framework = self.framework
        config = framework.config().load('wiz')
        BASEPATH = config.get("themepath", "themes")
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

    def theme(self, themename, layoutname, viewpath, view=None):
        framework = self.framework
        if self.is_dev(): cache = self.cache.wiz['dev_theme']
        else: cache = self.cache.wiz['prod_theme']

        namespace = f"{themename}/{layoutname}/{viewpath}"

        if namespace in cache and self.updateview==False:
            layout = cache[namespace]
        else:
            _, ext = os.path.splitext(viewpath)
            config = self.wizconfig
            BASEPATH = config.get("themepath", "themes")
            layoutbase = os.path.join(BASEPATH, themename, 'layout', layoutname)
            fs = framework.model("wizfs", module="wiz").use(layoutbase)
            layout = fs.read(viewpath)

            # get pug option
            if ext == ".pug":
                pugconfig = {}
                if self.wizconfig.pug is not None: 
                    pugconfig = self.wizconfig.pug

                pug = pypugjs.Parser(layout)
                pug = pug.parse()
                layout = pypugjs.ext.jinja.Compiler(pug, **pugconfig).compile()
            cache[namespace] = layout
        
        kwargs = framework.response.data.get()
        kwargs['wiz'] = self
        if view is not None:
            kwargs['view'] = view
        layout = framework.response.template_from_string(layout, **kwargs)
        return layout

    def __theme__(self, themename, layoutname, view):
        layout = self.theme(themename, layoutname, "layout.pug", view)
        return layout

    def render(self, *args, **kwargs):
        """render wiz interfaces.
        """
        if len(args) == 0: return ""
        view, _ = self.view(*args, **kwargs)
        return view

    def __view__(self, item, namespace, id, html, css, js, **kwargs):
        framework = self.framework
        kwargs['query'] = framework.request.query()
        fn_id = id + '_' + self.framework.lib.util.randomstring(12)
        html = html.split(">")
        if len(html) > 1:
            html = html[0] + f" id='wiz-{id}' ng-controller='wiz-{fn_id}'>" + ">".join(html[1:])
        else:
            html = f"<div id='wiz-{id}' ng-controller='wiz-{fn_id}'>" + ">".join(html) + "</div>"

        html = framework.response.template_from_string(html, **kwargs)
        
        o = "{"
        e = "}"
        kwargs = json.dumps(kwargs, default=self.json_default)
        kwargs = kwargs.encode('ascii')
        kwargs = base64.b64encode(kwargs)
        kwargs = kwargs.decode('ascii')

        reloaderjs = ""
        try:
            if self.DEVTOOLS:
                reloaderjs = RELOADJS.replace("__ID__", id)
        except:
            pass

        view = html
        view = view + f"\n{reloaderjs}<script src='/resources/wiz/libs/wiz.js'></script>\n<script type='text/javascript'>\nfunction __init_{fn_id}() {o} var wiz = season_wiz.load('{id}', '{fn_id}', '{namespace}');\n\n\nwiz.options = JSON.parse(atob('{kwargs}'));\n\n\n{js};\ntry {o} app.controller('wiz-{fn_id}', wiz_controller); {e} catch (e) {o} app.controller('wiz-{fn_id}', function() {o} {e} ); {e} {e}; __init_{fn_id}();\n</script>"
        view = view + f"\n<style>{css}</style>"
        return view

    def view(self, *args, **kwargs):
        id = args[0]
        namespace = id + ""
        if len(args) > 1: namespace = args[1]

        # check mode
        if self.is_dev(): 
            cache = self.cache.wiz['dev']
        else: 
            cache = self.cache.wiz['prod']

        # setup logger
        _prelogger = self.framework.log
        def _logger(*args):
            _prelogger(f"\033[94m[{namespace}]\033[0m", *args)
        self.framework.log = _logger

        # check cached view
        if namespace in cache and self.updateview==False:
            item, namespace, id, html, css, js, api, kwargs_code = cache[namespace]
            fn = {'__file__': 'season.Spawner', '__name__': 'season.Spawner', 'print': _logger}
            exec(compile(kwargs_code, 'season.Spawner', 'exec'), fn)
            _kwargs = fn['get'](self.framework, kwargs)
            kwargs = _kwargs

            self.framework.log = _prelogger
            return self.__view__(item, namespace, id, html, css, js, **kwargs), api

        # if view not in cahce, build view
        item = self.get(id=id)
        if item is None:
            item = self.get(namespace=id)
        if item is None:
            return None

        if namespace == id: namespace = item['namespace']

        id = item['id']
        html = item["html"]
        js = item["js"]
        css = item["css"]

        # build controller
        kwargs_code = "import season\nkwargs = season.stdClass()\ndef get(framework, kwargs):\n"
        kwargs_code_lines = item["kwargs"].split("\n")
        for tmp in kwargs_code_lines:
            kwargs_code = kwargs_code + "\n    " +  tmp
        kwargs_code = kwargs_code + "\n    return kwargs"
        fn = {'__file__': 'season.Spawner', '__name__': 'season.Spawner', 'print': _logger}
        exec(compile(kwargs_code, 'season.Spawner', 'exec'), fn)
        
        if self.updateview==False:
            _kwargs = fn['get'](self.framework, kwargs)
            kwargs = _kwargs

        o = "{"
        e = "}"

        # build html
        if item['properties']['html'] == 'pug':
            pugconfig = {}
            if self.wizconfig.pug is not None: pugconfig = self.wizconfig.pug
            pug = pypugjs.Parser(html)
            pug = pug.parse()
            html = pypugjs.ext.jinja.Compiler(pug, **pugconfig).compile()
        
        if item['properties']['css'] == 'less':
            css = f"#wiz-{id} {o} {css} {e}"
            css = lesscpy.compile(StringIO(css), minify=True)
            css = str(css)
        elif item['properties']['css'] == 'scss':
            css = f"#wiz-{id} {o} {css} {e}"
            css = sass.compile(string=css)
            css = str(css)

        if item['properties']['js'] == 'typescript':
            js = dukpy.typescript_compile(js)
            js = str(js)
            js = '\n'.join(js.split('\n')[5:-4])

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item['cachetime'] = timestamp
        cache[namespace] = (item, namespace, id, html, css, js, item['api'], kwargs_code)
        cache[id] = (item, namespace, id, html, css, js, item['api'], kwargs_code)

        self.framework.log = _prelogger
        return self.__view__(item, namespace, id, html, css, js, **kwargs), item['api']
