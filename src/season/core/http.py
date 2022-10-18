import season
from werkzeug.exceptions import HTTPException
import traceback

class ServiceHandler:
    def __init__(self, wiz):
        self.wiz = wiz

    def route(self, path):
        wiz = self.wiz
        workspace = wiz.workspace('service')

        request_uri = wiz.request.uri()
        route, segment = workspace.route.match(request_uri)
        if route.is_instance():
            route.proceed()

        # use dist on production mode
        fs = workspace.fs("www")
        if fs.exists():
            if wiz.dev() == False or wiz.server.is_bundle:
                if fs.isfile(path):
                    wiz.response.download(fs.abspath(path), as_attachment=False)
                if fs.exists("index.html"):
                    wiz.response.download(fs.abspath("index.html"), as_attachment=False)

        # code binding
        fs = workspace.build.distfs()
        if fs.isfile(path):
            wiz.response.download(fs.abspath(path), as_attachment=False)
        if fs.exists("index.html"):
            wiz.response.download(fs.abspath("index.html"), as_attachment=False)

    def asset(self, path):
        wiz = self.wiz
        build_resource = wiz.server.config.service.build_resource
        workspace = wiz.workspace('service')

        # code binding
        fs = workspace.fs("src", "assets")
        if fs.exists(path):
            filepath = fs.abspath(path)
            res = season.util.fn.call(build_resource, wiz=wiz, file=filepath)
            if res is not None:
                wiz.response.response(res)
            wiz.response.download(filepath, as_attachment=False)

        wiz.response.abort(404)

    def api(self, segment):
        wiz = self.wiz
        app_id = segment.id
        function = segment.function
        workspace = wiz.workspace('service')
        app = workspace.app(app_id)
        fn = app.api()
        if fn is not None and function in fn:
            season.util.fn.call(fn[function], wiz=wiz, segment=segment)
        wiz.response.status(404)

    def __call__(self):
        wiz = self.wiz
        
        # if asset request
        segment = wiz.request.match(wiz.uri.asset("<path:path>"))
        if segment is not None:
            self.asset(segment.path)

        # if api request
        segment = wiz.request.match(wiz.uri.wiz("api/<id>/<function>/<path:path>"))
        if segment is not None:
            self.api(segment)

        segment = wiz.request.match(wiz.uri.wiz("<path:path>"))
        if segment is not None:
            wiz.response.redirect(wiz.uri.ide())
        
        # if route
        segment = wiz.request.match(wiz.uri.base("<path:path>"))            
        if segment is None:
            self.route("")
        else:
            self.route(segment.path)

        wiz.response.abort(404)

class IdeHandler:
    def __init__(self, wiz):
        self.wiz = wiz
        wiz.mode.change("ide")

    def asset(self, path):
        wiz = self.wiz
        build_resource = wiz.server.config.service.build_resource
        workspace = wiz.workspace('ide')
        fs = workspace.fs("assets")
        if fs.exists(path):
            filepath = fs.abspath(path)
            res = season.util.fn.call(build_resource, wiz=wiz, file=filepath)
            if res is not None:
                wiz.response.response(res)
            wiz.response.download(filepath, as_attachment=False)
        wiz.response.abort(404)

    def route(self, path):
        wiz = self.wiz
        workspace = wiz.workspace('ide')

        # dist binding
        fs = workspace.build.distfs()
        if fs.isfile(path):
            wiz.response.download(fs.abspath(path), as_attachment=False)

        # default: index.html
        if fs.exists("index.html"):
            wiz.response.download(fs.abspath("index.html"), as_attachment=False)

    def api(self, segment):
        wiz = self.wiz
        app_id = segment.id
        function = segment.function
        workspace = wiz.workspace('ide')
        app = workspace.app(app_id)
        fn = app.api()
        if fn is not None and function in fn:
            season.util.fn.call(fn[function], wiz=wiz, segment=segment)
        wiz.response.status(404)

    def __call__(self):
        wiz = self.wiz

        # if request dev
        dev = wiz.request.query("dev", None)
        if dev is not None:
            if dev == "false" : wiz.dev.set(False)
            else: wiz.dev.set(True)
            wiz.response.redirect(wiz.request.uri())

        branch = wiz.request.query("branch", None)
        if branch is not None and len(branch) > 0:
            if branch in wiz.branch.list():
                wiz.branch(branch)
            wiz.response.redirect(wiz.request.uri())

        season.util.fn.call(wiz.server.config.ide.acl, wiz=wiz)

        # if asset request
        segment = wiz.request.match(wiz.uri.asset("<path:path>"))
        if segment is not None:
            self.asset(segment.path)

        # if api request
        segment = wiz.request.match("/api/<id>/<function>/<path:path>")
        if segment is not None:
            self.api(segment)
        
        # if route
        segment = wiz.request.match("/<path:path>")
        path = ""
        if segment is not None:
            path = segment.path
        self.route(path)

class HTTP:
    def __init__(self, server):
        self.server = server

    def bind(self):
        app = self.server.app.flask
        config = self.server.config
        HTTP_METHODS = config.boot.allowed_method

        @app.after_request
        def after_request(response):
            wiz = self.server.wiz()
            res = season.util.fn.call(config.service.after_request, response=response, wiz=wiz)
            if res is not None: 
                return res
            return response

        @app.errorhandler(season.core.exception.ResponseException)
        def handle_response(e):
            wiz = self.server.wiz()
            code, response = e.get_response()
            wiz.tracer.code = code
            logger = wiz.logger()
            logger(wiz.request.uri(), level=season.LOG_DEBUG)
            return response, code

        @app.errorhandler(season.core.exception.ErrorException)
        @app.errorhandler(season.core.exception.CompileException)
        @app.errorhandler(HTTPException)
        @app.errorhandler(Exception)
        def handle_exception(e):
            wiz = self.server.wiz()
            code = wiz.response.status_code
            if code is None: code = 500
            wiz.tracer.code = code
            errormsg = wiz.request.uri() + "\n" + traceback.format_exc()
            logger = wiz.logger()

            if isinstance(e, HTTPException):
                logger(errormsg, level=season.LOG_WARNING)
            else:
                logger(errormsg, level=season.LOG_ERROR)

            try:
                season.util.fn.call(config.service.on_error, wiz=wiz, error=e, e=e)
            except season.core.exception.ResponseException as e1:
                code, response = e1.get_response()
                return response, code

            try:
                return e.get_response()
            except:
                pass

            return '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><title>500 Internal Server Error</title><h1>Internal Server Error</h1><p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>', 500

        # HTTP Routing spec
        # - /<baseuri>/<path:path> : ide interface, baseuri default /
        # - /<wiz>/api/<app_id>/<function_name>/<segment> : app api
        # - /<wiz>/ide : ide interface
        # - /<wiz>/ide/api/<app_id>/<function_name>/<segment> : ide app api 

        @app.route("/", methods=HTTP_METHODS)
        @app.route("/<path:path>", methods=HTTP_METHODS)
        def request_handler(*args, **kwargs):
            wiz = self.server.wiz()

            request_uri = wiz.request.request().path

            # change ide mode
            handler = None
            if self.server.is_bundle == False:
                ideuri = wiz.uri.ide()
                if request_uri[:len(ideuri) + 1] == ideuri + "/" or ideuri == request_uri:
                    handler = IdeHandler(wiz)
                
            if handler is None:
                handler = ServiceHandler(wiz)

            handler()

            wiz.response.abort(404)