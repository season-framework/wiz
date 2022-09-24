import season
from werkzeug.exceptions import HTTPException
import traceback

class ServiceHandler:
    def __init__(self, wiz):
        self.wiz = wiz

    def route(self, path):
        wiz = self.wiz
        workspace = wiz.workspace('service')

        # TODO: route policy

        # dist binding
        fs = workspace.fs("dist")
        if fs.isfile(path):
            wiz.response.download(fs.abspath(path), as_attachment=False)

        # default: index.html
        wiz.response.download(fs.abspath("index.html"), as_attachment=False)

    def asset(self, path):
        wiz = self.wiz
        build_resource = wiz.server.config.service.build_resource
        workspace = wiz.workspace('service')
        fs = workspace.fs("asset")
        if fs.exists(path):
            filepath = fs.abspath(path)
            res = season.util.fn.call(build_resource, wiz=wiz, file=filepath)
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

    def app(self, path):
        wiz = self.wiz
        
        if path is None: 
            path = ""
        
        workspace = wiz.workspace('ide')
        wiz.response.status(200, workspace.path())

    def __call__(self):
        wiz = self.wiz
        
        segment = wiz.request.match("/<action>/<path:path>")
        action = segment.action
        if action == 'app':
            self.app(segment.path)
        elif action == 'asset':
            pass
        elif action == 'api':
            pass

        wiz.response.abort(404)

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

        @app.route("/", methods=HTTP_METHODS)
        @app.route("/<path:path>", methods=HTTP_METHODS)
        def request_handler(*args, **kwargs):
            wiz = self.server.wiz()

            request_uri = wiz.request.request().path

            # change ide mode
            ideuri = wiz.uri.ide()
            if request_uri[:len(ideuri) + 1] == ideuri + "/" or ideuri == request_uri:
                wiz.mode.change("ide")
                handler = IdeHandler(wiz)
            else:
                handler = ServiceHandler(wiz)

            handler()
            wiz.response.abort(404)