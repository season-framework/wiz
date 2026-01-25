import season

class IdeHandler:
    def __init__(self, wiz):
        self.wiz = wiz

    def asset(self, path):
        wiz = self.wiz
        on_asset = wiz.server.config.boot.event.on_asset
        fs = wiz.ide.fs("assets")
        if fs.exists(path):
            filepath = fs.abspath(path)
            res = season.util.compiler(on_asset).call(wiz=wiz, file=filepath)
            if res is not None:
                wiz.response.response(res)
            wiz.response.download(filepath, as_attachment=False)
        wiz.response.abort(404)

    def route(self, path):
        wiz = self.wiz

        # dist binding
        fs = wiz.ide.fs("build", "dist", "build")
        if fs.isfile(path):
            wiz.response.download(fs.abspath(path), as_attachment=False)

        # default: index.html
        if fs.exists("index.html"):
            wiz.response.download(fs.abspath("index.html"), as_attachment=False)

    def api(self, segment):
        wiz = self.wiz
        app_id = segment.id
        function = segment.function

        wiz.ide.plugin = wiz.ide.plugin(app_id.split(".")[0])
        fn = wiz.ide.api(app_id)

        if fn is not None and function in fn:
            season.util.compiler(fn[function]).call(wiz=wiz, segment=segment)
        
        wiz.response.status(404)

    def __call__(self):
        wiz = self.wiz

        # if request dev
        dev = wiz.ide.request.query("dev", None)
        if dev is not None:
            if dev == "false" : wiz.project.dev(False)
            else: wiz.project.dev(True)
            wiz.response.redirect(wiz.uri.ide() + "/ide")

        # if request project
        project = wiz.ide.request.query("project", None)
        if project is not None and len(project) > 0:
            if project in wiz.project.list():
                wiz.project.checkout(project)
            wiz.response.redirect(wiz.uri.ide() + "/ide")

        # check acl
        season.util.compiler(wiz.server.config.ide.acl).call(wiz=wiz)

        # if asset request
        segment = wiz.ide.request.match(wiz.uri.asset("<path:path>"))
        if segment is not None:
            self.asset(segment.path)

        # if api request
        segment = wiz.ide.request.match("/api/<id>/<function>/<path:path>")
        if segment is not None:
            self.api(segment)
        
        # if route
        segment = wiz.ide.request.match("/<path:path>")
        path = ""
        if segment is not None:
            path = segment.path

        self.route(path)
