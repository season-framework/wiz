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

class Model(season.core.interfaces.model.MySQL):
    def __init__(self, framework):
        super().__init__(framework)
        self.framework = framework 
        self.namespace = 'wiz'

        self.cache = framework.cache
        if 'wiz' not in self.cache: 
            self.cache.wiz = season.stdClass()
            self.cache.wiz.dev = season.stdClass()
            self.cache.wiz.prod = season.stdClass()

        config = framework.config.load("wiz")
        self.tablename = config.get("table", "wiz")
        self.wizsrc = config.get("wizsrc", os.path.join(framework.core.PATH.MODULES, "wiz", "wizsrc"))
        try:
            self.DEVMODE = framework.request.cookies("season-wiz-devmode", "false")
            if self.DEVMODE == "false": self.DEVMODE = False
            else: self.DEVMODE = True
        except:
            self.DEVMODE = False
        self.updateview = False
        self.wizconfig = config

    def set_update_view(self, updateview):
        self.updateview = updateview
    
    def is_dev(self):
        return self.DEVMODE

    def set_dev(self, DEVMODE):
        self.framework.response.cookies.set("season-wiz-devmode", DEVMODE)
        if DEVMODE == "false": self.DEVMODE = False
        else: DEVMODE = True

    def upsert(self, values, **format):
        res = super().upsert(values, **format)
        self.set_update_view(True)
        self.cache.wiz = season.stdClass()
        self.cache.wiz.dev = season.stdClass()
        self.cache.wiz.prod = season.stdClass()

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

        return res

    def route(self):
        framework = self.framework
        
        requri = framework.request.uri()
        app_id = None
        theme = None

        if requri.startswith("/wiz/"):
            return

        routes = self.routes()
        
        app_id, theme, segment = routes(requri)
        if app_id is None:
            return
        
        framework.request.segment = season.stdClass(segment)

        view = self.render(app_id)
        config = framework.config.load("wiz")
        if 'default' not in config.theme:
            config.theme.default = season.stdClass()
            config.theme.default.module = "wiz/theme"
            config.theme.default.view = "layout-wiz.pug"
        
        if theme not in config.theme:
            for key in config.theme:
                theme = key
                break
        
        theme = config.theme[theme]
        framework.response.render(theme.view, module=theme.module, view=view, app_id=app_id)

    def routes(self):
        if self.DEVMODE:
            if 'routes' in self.cache.wiz.dev and self.updateview==False:
                return self.cache.wiz.dev.routes
        else:
            if 'routes' in self.cache.wiz.prod and self.updateview==False:
                return self.cache.wiz.prod.routes
            
        routes = self.select(fields="id,route,theme", orderby="`updated` DESC")
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
            self.cache.wiz.dev.routes = matcher
            return self.cache.wiz.dev.routes
        else:
            self.cache.wiz.prod.routes = matcher
            return self.cache.wiz.prod.routes
        
    def render(self, *args, **kwargs):
        if len(args) == 0: return ""
        view, _ = self.view(*args, **kwargs)
        return view

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
                kwargs['version'] = {"op": "!=", "value": "master"}
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

    def _view(self, item, namespace, id, html, css, js, **kwargs):
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
            config = framework.config.load("wiz")
            if config.devtools:
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

        if self.DEVMODE: cache = self.cache.wiz.dev
        else: cache = self.cache.wiz.prod

        if namespace in cache and self.updateview==False:
            item, namespace, id, html, css, js, api, fn = cache[namespace]

            _prelogger = self.framework.log
            def _logger(*args):
                _prelogger(f"[{namespace}]", *args)
            self.framework.log = _logger

            _kwargs = fn['get'](self.framework, kwargs)
            kwargs = _kwargs
            return self._view(item, namespace, id, html, css, js, **kwargs), api

        item = self.get(id=id)
        if item is None:
            item = self.get(namespace=id)
        if item is None:
            return None

        if namespace == id: namespace = item['namespace']
        _prelogger = self.framework.log
        def _logger(*args):
            _prelogger(f"[{namespace}]", *args)
        self.framework.log = _logger

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

        cache[namespace] = (item, namespace, id, html, css, js, item['api'], fn)
        cache[id] = (item, namespace, id, html, css, js, item['api'], fn)
        return self._view(item, namespace, id, html, css, js, **kwargs), item['api']
