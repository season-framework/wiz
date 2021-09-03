import season
import lesscpy
from six import StringIO

class Model(season.core.interfaces.model.MySQL):
    def __init__(self, framework):
        super().__init__(framework)
        self.namespace = 'wiz'
        config = framework.config.load("wiz")
        self.tablename = config.get("table", "wiz")        

    def view(self, id):
        item = self.get(id=id)
        if item is None:
            item = self.get(namespace=id)
        if item is None:
            return None

        id = item['id']
        
        html = item["html"]
        js = item["js"]
        css = item["css"]
        
        o = "{"
        e = "}"

        css = f"#wiz-{id} {o} {css} {e}"
        css = lesscpy.compile(StringIO(css), minify=True)
        css = str(css)

        html = html.split(">")
        html = html[0] + f" id='wiz-{id}' ng-controller='wiz-{id}'>" + ">".join(html[1:])

        view = html
        view = view + f"<script>function __init_{id}() {o} var wiz = season_wiz('{id}'); {js}; try {o} app.controller('wiz-{id}', wiz_controller); {e} catch (e) {o} app.controller('wiz-{id}', function() {o} {e} ); {e} {e}; __init_{id}();</script>"
        view = view + f"<style>{css}</style>"
        return view
