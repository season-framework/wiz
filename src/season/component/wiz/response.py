import os
import season
from werkzeug.routing import Map, Rule

from season.component.base.response import Response as Base

class Response(Base):
    def __init__(self, wiz):
        super().__init__(wiz)

    def redirect(self, url):
        self.status_code = 302
        resp = self._flask.redirect(url)
        return self._build(resp)

    def render(self, *args, **kwargs):
        wiz = self.wiz
        if len(args) == 0:
            return self
        if len(args) == 1:
            app_id = args[0]
        else:
            route = args[0]
            endpoint = args[1]

            if route is None: return self
            if len(route) == 0: return self
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
                    
            request_uri = wiz.request.uri()
            app_id, segment = matcher(request_uri)
            wiz.request.segment = season.stdClass(**segment)

        if app_id is None:
            return self

        app = wiz.app(app_id)
        view = app.view(app_id, **kwargs)

        render_theme = app.data(False)['package']['theme']        
        render_theme = render_theme.split("/")
        themename = render_theme[0]
        layoutname = render_theme[1]

        fs = season.util.os.FileSystem(season.path.lib)
        wizjs = fs.read(os.path.join('component', 'wiz.js'))
        wizurl = wiz.server.config.server.wiz_url
        if wizurl[-1] == "/": wizurl = wizurl[:-1]
        wizjs = wizjs.replace("{$BASEPATH$}", wizurl + "/api").replace("{$URL$}", wizurl).replace("{$SOCKETBASEPATH$}", wizurl + "/app/" + wiz.branch())
        view = f'<script type="text/javascript">{wizjs}</script>\n{view}'

        view = wiz.theme(themename).layout(layoutname).view('layout.pug', view)
        
        self.send(view, "text/html")
