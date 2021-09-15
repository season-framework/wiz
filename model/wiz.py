import season
import lesscpy
from six import StringIO
import json
import os
import pypugjs
import datetime

class Model(season.core.interfaces.model.MySQL):
    def __init__(self, framework):
        super().__init__(framework)
        self.namespace = 'wiz'
        config = framework.config.load("wiz")
        self.tablename = config.get("table", "wiz")
        self.wizsrc = config.get("wizsrc", os.path.join(framework.core.PATH.MODULES, "wiz", "wizsrc"))
        self.updateview = False
        self.wizconfig = config

    def set_update_view(self, updateview):
        self.updateview = updateview

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
        view = view + f"<script src='/resources/wiz/libs/wiz.js'></script><script>function __init_{fn_id}() {o} var wiz = season_wiz.load('{id}', '{fn_id}', '{namespace}'); wiz.options = {kwargs}; {js}; try {o} app.controller('wiz-{fn_id}', wiz_controller); {e} catch (e) {o} app.controller('wiz-{fn_id}', function() {o} {e} ); {e} {e}; __init_{fn_id}();</script>"
        view = view + f"<style>{css}</style>"
        return view

    def view(self, *args, **kwargs):
        id = args[0]
        namespace = id + ""
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
            _kwargs = fn['get'](self.framework, kwargs)
            kwargs = _kwargs
        except Exception as e:
            pass

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

        if len(args) > 1: namespace = args[1]
        return self._view(namespace, id, html, css, js, **kwargs), item['api']

    def view_from_source(self, *args, **kwargs):
        id = args[0]
        namespace = args[0]
        framework = self.framework
    
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
        return self._view(namespace, id, html, css, js, **kwargs), api