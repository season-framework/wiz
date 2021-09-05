import season
import lesscpy
from six import StringIO
import json
import os
import pypugjs

class Model(season.core.interfaces.model.MySQL):
    def __init__(self, framework):
        super().__init__(framework)
        self.namespace = 'wiz'
        config = framework.config.load("wiz")
        self.tablename = config.get("table", "wiz")
        self.wizsrc = config.get("wizsrc", os.path.join(framework.core.PATH.MODULES, "wiz", "wizsrc"))

    def render(self, id, render="webadmin", **kwargs):
        kwargs['render'] = render

        if render == 'source':
            view, _ = self.view_from_source(id, **kwargs)
        else:
            view, _ = self.view(id, **kwargs)
        return view

    def _view(self, id, html, css, js, **kwargs):
        framework = self.framework
        
        try:
            pug = pypugjs.Parser(html)
            pug = pug.parse()
            pug = pypugjs.ext.jinja.Compiler(pug).compile()
            html = framework.response.template_from_string(pug, **kwargs)
        except:
            pass

        o = "{"
        e = "}"

        css = f"#wiz-{id} {o} {css} {e}"
        css = lesscpy.compile(StringIO(css), minify=True)
        css = str(css)

        html = html.split(">")

        if len(html) > 1:
            html = html[0] + f" id='wiz-{id}' ng-controller='wiz-{id}'>" + ">".join(html[1:])
            kwargs = json.dumps(kwargs, default=season.json_default)
        else:
            html = f"<div id='wiz-{id}' ng-controller='wiz-{id}'>" + ">".join(html) + "</div>"

        fn_id = self.framework.lib.util.randomstring(32)

        view = html
        view = view + f"<script src='/resources/wiz/libs/wiz.js'></script><script>function __init_{fn_id}() {o} var wiz = season_wiz('{id}'); wiz.options = {kwargs}; {js}; try {o} app.controller('wiz-{id}', wiz_controller); {e} catch (e) {o} app.controller('wiz-{id}', function() {o} {e} ); {e} {e}; __init_{fn_id}();</script>"
        view = view + f"<style>{css}</style>"
        return view

    def view(self, id, **kwargs):
        item = self.get(id=id)
        if item is None:
            item = self.get(namespace=id)
        if item is None:
            return None

        id = item['id']
        html = item["html"]
        js = item["js"]
        css = item["css"]
        
        return self._view(id, html, css, js, **kwargs), item['api']

    def view_from_source(self, id, **kwargs):
        framework = self.framework
    
        html = ""
        css = ""
        js = ""
        api = ""

        basepath = os.path.join(self.wizsrc, id)

        if os.path.isdir(basepath) == False:
            return self._view(id, html, css, js, **kwargs), api

        wizfs = framework.model("wizfs", module="wiz")
        wizfs.set_namespace(id)

        html = wizfs.read("view.pug")
        css = wizfs.read("view.less")
        js = wizfs.read("view.js")
        api = wizfs.read("view.py")

        return self._view(id, html, css, js, **kwargs), api