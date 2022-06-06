from werkzeug.exceptions import HTTPException
import traceback

import season
from season.core.lib.server.handler.http.base import Base

class Trigger(Base):
    def route(self, wiz, app, config):
        @app.before_request
        def before_request():
            wiz.trace()
            if config.wiz.before_request is not None:
                season.util.fn.call(config.wiz.before_request, wiz=wiz)

        @app.after_request
        def after_request(response):
            if config.wiz.after_request is not None:
                res = season.util.fn.call(config.wiz.after_request, response=response, wiz=wiz)
                if res is not None: return res
            return response

class Response(Base):
    def route(self, wiz, app, config):
        @app.errorhandler(season.exception.ResponseException)
        def handle_response(e):
            tracer = wiz.tracer
            tracer.code = wiz.response.status_code
            wiz.log(tracer.path, level=season.log.debug)
            code, response = e.get_response()
            return response, code

class Error(Base):
    def route(self, wiz, app, config):
        def error_handler(e):
            try:
                uri = wiz.request.uri()
                if uri[:len(wiz.wizurl)] == wiz.wizurl:
                    wiz.response.redirect(wiz.wizurl)
                if wiz.server.config.wiz.on_error is not None: 
                    season.util.fn.call(wiz.server.config.wiz.on_error, wiz=wiz, error=e, e=e)
            except season.exception.ResponseException as e1:
                code, response = e1.get_response()
                return response, code
            return None

        # Controlled Exception Error
        @app.errorhandler(season.exception.ErrorException)
        def handle_exception_error(e):
            tracer = wiz.tracer
            code = wiz.response.status_code
            if code is None: code = 500
            tracer.code = code
            errormsg = tracer.path + "\n" + tracer.error
            wiz.log(errormsg, level=season.log.error, color=91)
            res = error_handler(e)
            if res is not None: return res
            return e.get_response()

        @app.errorhandler(season.exception.CompileException)
        def handle_exception_compile_error(e):
            tracer = wiz.tracer
            code = wiz.response.status_code
            if code is None: code = 500
            tracer.code = code
            errormsg = tracer.path + "\n" + e.message + "\n" + "file: " + e.filename
            wiz.log(errormsg, level=season.log.error, color=91)
            res = error_handler(e)
            if res is not None: return res
            return e.get_response()

        # HTTP Exception Handler 
        @app.errorhandler(HTTPException)
        def handle_exception_http(e):
            tracer = wiz.tracer
            tracer.code = e.code
            errormsg = tracer.path
            wiz.log(errormsg, level=season.log.warning, color=93)
            res = error_handler(e)
            if res is not None: return res
            return e.get_response()

        # Internal Error Handler
        @app.errorhandler(Exception)
        def handle_exception(e):            
            tracer = wiz.tracer
            tracer.code = 500
            errormsg = tracer.path + "\n" + traceback.format_exc()
            wiz.log(errormsg, level=season.log.critical, color=91)
            res = error_handler(e)
            if res is not None: return res
            return '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><title>500 Internal Server Error</title><h1>Internal Server Error</h1><p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>', 500
