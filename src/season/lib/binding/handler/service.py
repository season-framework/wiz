import season

class ServiceHandler:
    def __init__(self, wiz):
        self.wiz = wiz

    def route(self, path):
        wiz = self.wiz

        # filter binding
        wiz.project.filter()

        # dist binding
        fs = wiz.project.fs("bundle", "www")
        if fs.isfile(path):
            wiz.response.download(fs.abspath(path), as_attachment=False)

        # default: index.html
        if fs.exists("index.html"):
            wiz.response.download(fs.abspath("index.html"), as_attachment=False)

    def asset(self, path):
        wiz = self.wiz
        on_asset = wiz.server.config.boot.event.on_asset

        # code binding
        fs = wiz.project.fs("bundle", "src", "assets")

        if fs.exists(path):
            filepath = fs.abspath(path)
            res = season.util.compiler(on_asset).call(wiz=wiz, file=filepath)
            if res is not None:
                wiz.response.response(res)
            wiz.response.download(filepath, as_attachment=False)

        wiz.response.abort(404)

    def __call__(self):
        wiz = self.wiz
        
        # if asset request
        segment = wiz.request.match(wiz.uri.asset("<path:path>"))
        if segment is not None:
            self.asset(segment.path)

        # if api request
        if wiz.request.uri() == wiz.uri.ide():
            if wiz.server.config.boot.bundle:
                wiz.response.redirect("/")
            wiz.response.redirect(wiz.uri.ide("ide"))

        # if route
        segment = wiz.request.match(wiz.uri.base("<path:path>"))
        if segment is None:
            self.route("")
        else:
            self.route(segment.path)

        wiz.response.abort(404)