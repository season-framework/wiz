import season
import lesscpy
from six import StringIO
import json
import os
import pypugjs
import datetime
import re
from werkzeug.routing import Map, Rule

class Model(season.core.interfaces.model.MySQL):
    def __init__(self, framework):
        super().__init__(framework)
        self.framework = framework 
        self.namespace = 'wiz'

        self.cache = framework.cache
        if 'wiz' not in self.cache: self.cache.wiz = season.stdClass()

        config = framework.config.load("wiz")
        self.tablename = config.get("table", "wiz")
        self.wizsrc = config.get("wizsrc", os.path.join(framework.core.PATH.MODULES, "wiz", "wizsrc"))
        self.updateview = False
        self.wizconfig = config

    def set_update_view(self, updateview):
        self.updateview = updateview

    def upsert(self, values, **format):
        res = super().upsert(values, **format)
        self.set_update_view(True)
        self.cache.wiz = season.stdClass()

        if 'route' not in values or len(values['route']) == 0:
            self.render(values['id'])
        else:
            self.routes()
            self.route()
            self.framework.request.segment = season.stdClass()
            self.render(values['id'])

        return res

    def route(self):
        framework = self.framework
        routes = self.routes()

        app_id = None
        theme = None
        requri = framework.request.uri()

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
        if 'routes' in self.cache.wiz and self.updateview==False:
            return self.cache.wiz.routes
            
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

        self.cache.wiz.routes = matcher
        return self.cache.wiz.routes
        
    def render(self, *args, **kwargs):
        if len(args) == 0: return ""
        if 'render' not in kwargs: kwargs['render'] = "webadmin"
        render = kwargs['render']
        if render == 'source':
            view, _ = self.view_from_source(*args, **kwargs)
        else:
            view, _ = self.view(*args, **kwargs)
        return view

    def json_default(self, value):
        if isinstance(value, datetime.date): 
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return ""

    def _view(self, namespace, id, html, css, js, **kwargs):
        framework = self.framework
        kwargs['query'] = framework.request.query()
        fn_id = id + '_' + self.framework.lib.util.randomstring(12)

        html = html.split(">")
        if len(html) > 1:
            html = html[0] + f" id='wiz-{id}' ng-controller='wiz-{fn_id}'>" + ">".join(html[1:])
        else:
            html = f"<div id='wiz-{id}' ng-controller='wiz-{fn_id}'>" + ">".join(html) + "</div>"

        try:
            html = framework.response.template_from_string(html, **kwargs)
        except:
            pass

        o = "{"
        e = "}"
        kwargs = json.dumps(kwargs, default=self.json_default)
        view = html
        view = view + f"\n<script src='/resources/wiz/libs/wiz.js'></script>\n<script type='text/javascript'>\n<!--\nfunction __init_{fn_id}() {o} var wiz = season_wiz.load('{id}', '{fn_id}', '{namespace}');\n\n\nwiz.options = {kwargs};\n\n\n{js};\ntry {o} app.controller('wiz-{fn_id}', wiz_controller); {e} catch (e) {o} app.controller('wiz-{fn_id}', function() {o} {e} ); {e} {e}; __init_{fn_id}();\n-->\n</script>"
        view = view + f"\n<style>{css}</style>"
        return view

    def view(self, *args, **kwargs):
        id = args[0]
        namespace = id + ""

        if namespace in self.cache.wiz and self.updateview==False:
            namespace, id, html, css, js, api, fn = self.cache.wiz[namespace]
            _kwargs = fn['get'](self.framework, kwargs)
            kwargs = _kwargs
            return self._view(namespace, id, html, css, js, **kwargs), api

        item = self.get(id=id)
        if item is None:
            item = self.get(namespace=id)
        if item is None:
            return None

        id = item['id']
        html = item["html"]
        js = item["js"]
        css = item["css"]

        try:
            kwargs_code = "import season\nkwargs = season.stdClass()\ndef get(framework, kwargs):\n"
            kwargs_code_lines = item["kwargs"].split("\n")
            for tmp in kwargs_code_lines:
                kwargs_code = kwargs_code + "\n    " +  tmp
            kwargs_code = kwargs_code + "\n    return kwargs"
            fn = {'__file__': 'season.Spawner', '__name__': 'season.Spawner'}
            exec(compile(kwargs_code, 'season.Spawner', 'exec'), fn)
        except Exception as e:
            pass

        if self.updateview==False:
            _kwargs = fn['get'](self.framework, kwargs)
            kwargs = _kwargs

        # build
        if item['build_html'] is None or self.updateview == True:
            o = "{"
            e = "}"

            try:
                pugconfig = {}
                if self.wizconfig.pug is not None: pugconfig = self.wizconfig.pug
                pug = pypugjs.Parser(html)
                pug = pug.parse()
                html = pypugjs.ext.jinja.Compiler(pug, **pugconfig).compile()
            except:
                pass
            
            css = f"#wiz-{id} {o} {css} {e}"
            css = lesscpy.compile(StringIO(css), minify=True)
            css = str(css)

            data = dict()
            data['build_html'] = html
            data['build_css'] = css
            self.update(data, id=id)
        else:
            html = item['build_html']
            css = item['build_css']

        ns = namespace
        if len(args) > 1: ns = args[1]

        self.cache.wiz[namespace] = (ns, id, html, css, js, item['api'], fn)
        return self._view(ns, id, html, css, js, **kwargs), item['api']

    def view_from_source(self, *args, **kwargs):
        id = args[0]
        namespace = args[0]
        framework = self.framework

        if namespace in self.cache.wiz and self.updateview==False:
            namespace, id, html, css, js, api = self.cache.wiz[namespace]
            return self._view(namespace, id, html, css, js, **kwargs), api
    
        html = ""
        css = ""
        js = ""
        api = ""

        basepath = os.path.join(self.wizsrc, id)

        if os.path.isdir(basepath) == False:
            return self._view(namespace, id, html, css, js, **kwargs), api

        wizfs = framework.model("wizfs", module="wiz")
        wizfs.set_namespace(id)

        html = wizfs.read("view.pug")
        css = wizfs.read("view.less")
        js = wizfs.read("view.js")
        api = wizfs.read("view.py")

        # build
        o = "{"
        e = "}"

        try:
            pugconfig = {}
            if self.wizconfig.pug is not None: pugconfig = self.wizconfig.pug
            pug = pypugjs.Parser(html)
            pug = pug.parse()
            html = pypugjs.ext.jinja.Compiler(pug, **pugconfig).compile()
        except:
            pass

        try:
            html = framework.response.template_from_string(html, **kwargs)
        except:
            pass

        css = f"#wiz-{id} {o} {css} {e}"
        css = lesscpy.compile(StringIO(css), minify=True)
        css = str(css)

        if len(args) > 1: namespace = args[1]

        self.cache.wiz[namespace] = (namespace, id, html, css, js, api)
        return self._view(namespace, id, html, css, js, **kwargs), api