import season
from werkzeug.exceptions import HTTPException
import traceback

class HTTP:
    def __init__(self, server):
        app = server.app.flask
        HTTP_METHODS = server.config.boot.allowed_method

        # initialize wiz instance on request flow
        @app.before_request
        def before_request():
            wiz = server.wiz()
            season.util.compiler(server.config.boot.event.before_request).call(wiz=wiz)

        # after request
        @app.after_request
        def after_request(response):
            wiz = server.wiz()
            res = season.util.compiler(server.config.boot.event.after_request).call(response=response, wiz=wiz)
            if res is not None: 
                return res
            return response

        @app.errorhandler(season.lib.exception.ResponseException)
        def handle_response(e):
            wiz = server.wiz()
            code, response = e.get_response()            
            logger = wiz.logger("http", "resp")
            logger(wiz.request.uri(), level=season.LOG_DEBUG)

            return response, code

        @app.errorhandler(season.lib.exception.ErrorException)
        @app.errorhandler(season.lib.exception.CompileException)
        @app.errorhandler(HTTPException)
        @app.errorhandler(Exception)
        def handle_exception(e):
            wiz = server.wiz()
            code = wiz.response.status_code
            if code is None: code = 500
            errormsg = wiz.request.uri() + "\n" + traceback.format_exc()
            
            logger = wiz.logger("http", "error")
            if isinstance(e, HTTPException):
                logger(errormsg, level=season.LOG_WARNING)
            else:
                logger(errormsg, level=season.LOG_ERROR)

            try:
                season.util.compiler(server.config.boot.event.on_error).call(wiz=wiz, error=e, e=e)
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
            wiz = server.wiz()

            request_uri = wiz.request.uri()
            handler = None

            # if ide request
            ideuri = wiz.uri.ide("ide")
            if request_uri[:len(ideuri) + 1] == ideuri + "/" or ideuri == request_uri:  
                handler = season.lib.binding.handler.ide(wiz)
            
            # if service request
            if handler is None:
                handler = season.lib.binding.handler.service(wiz)
            
            handler()
            wiz.response.abort(404)