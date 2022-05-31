import os
import season
import time
import traceback
from werkzeug.exceptions import HTTPException

class HTTP:
    def __init__(self, server):
        self.server = server

    def trigger(self):
        wiz = self.server.wiz
        app = self.server.app
        config = self.server.config

        @app.before_request
        def before_request():
            wiz.trace()
            if config.server.before_request is not None:
                season.util.fn.call(config.server.before_request, wiz=wiz)

        @app.after_request
        def after_request(response):
            if config.server.after_request is not None:
                res = season.util.fn.call(config.server.after_request, response=response, wiz=wiz)
                if res is not None: return res
            return response

    def response(self):
        wiz = self.server.wiz
        app = self.server.app

        @app.errorhandler(season.exception.ResponseException)
        def handle_response(e):
            tracer = wiz.tracer
            code = wiz.response.status_code
            if code is None: code = 200
            tags = [tracer.branch, "response", code]
            wiz.log(tracer.path, level=season.log.info, tags=tags)
            code, response = e.get_response()
            return response, code

    def error(self):
        app = self.server.app
        wiz = self.server.wiz

        # Controlled Exception Error
        @app.errorhandler(season.exception.ErrorException)
        def handle_exception_error(e):
            tracer = wiz.tracer
            code = wiz.response.status_code
            if code is None: code = 500
            tags = [tracer.branch, code]
            errormsg = tracer.path + "\n" + tracer.error
            wiz.log(errormsg, level=season.log.error, tags=tags, color=91)
            return e.get_response()

        # HTTP Exception Handler 
        @app.errorhandler(HTTPException)
        def handle_exception_http(e):
            tracer = wiz.tracer
            tags = [tracer.branch, e.code]
            errormsg = tracer.path
            wiz.log(errormsg, level=season.log.warning, tags=tags, color=93)
            return e.get_response()

        # Internal Error Handler
        @app.errorhandler(Exception)
        def handle_exception(e):
            tracer = wiz.tracer
            tags = [tracer.branch, 500]
            errormsg = tracer.path + "\n" + traceback.format_exc()
            wiz.log(errormsg, level=season.log.critical, tags=tags, color=91)
            return '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><title>500 Internal Server Error</title><h1>Internal Server Error</h1><p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>', 500

    def resources(self):
        app = self.server.app
        wiz = self.server.wiz

        @app.route('/resources')
        @app.route('/resources/')
        @app.route('/resources/<path:path>')
        def resources_handler(*args, **kwargs):
            try:
                branch = wiz.branch()

                path = wiz.request.uri()
                path = "/".join(path.split("/")[2:])
                segment = path.split("/")
                target = segment[0]

                # global resources (priority high)
                filepath = os.path.join(season.path.project, "branch", branch, "resources", "/".join(segment))

                # access resources in theme
                if os.path.isfile(filepath) == False and target == 'themes':
                    segment = segment[1:]
                    themename = segment[0]
                    segment = segment[1:]
                    filepath = os.path.join(season.path.project, "branch", branch, "themes", themename, "resources", "/".join(segment))

                if os.path.isfile(filepath):
                    dirname = os.path.dirname(filepath)
                    filename = os.path.basename(filepath)

                    if wiz.server.config.server.build_resource is not None:
                        res = season.util.fn.call(wiz.server.config.server.build_resource, wiz=wiz, resource_dirpath=dirname, resource_filepath=filename)
                        if res is not None: return res

                    response = wiz.server.flask.send_from_directory(dirname, filename)
                    raise season.exception.ResponseException(200, response)
            except season.exception.ResponseException as e:
                raise e
            except Exception as e:
                wiz.tracer.error = traceback.format_exc()
                raise season.exception.ErrorException()

            wiz.response.abort(404)

    def route(self):
        config = self.server.config
        app = self.server.app
        wiz = self.server.wiz
        HTTP_METHODS = config.server.http_method

        @app.route("/", methods=HTTP_METHODS)
        @app.route("/<string:module>", methods=HTTP_METHODS)
        @app.route("/<string:module>/", methods=HTTP_METHODS)
        @app.route("/<string:module>/<path:path>", methods=HTTP_METHODS)
        def request_handler(*args, **kwargs):
            try:
                path = wiz.request.uri()
                app, segment = wiz.route.match(path)

                if app is not None:
                    wiz.request.segment = season.stdClass(**segment)
                    app.proceed()
            except season.exception.ResponseException as e:
                raise e
            except Exception as e:
                wiz.tracer.error = traceback.format_exc()
                raise season.exception.ErrorException()

            wiz.response.abort(404)

    def wiz(self):
        config = self.server.config
        app = self.server.app
        wiz = self.server.wiz

        HTTP_METHODS = config.server.http_method
        wizurl = config.wiz.url
        if wizurl[-1] == "/": wizurl = wizurl[:-1]

        # base request path
        @app.route(wizurl, methods=HTTP_METHODS)
        @app.route(wizurl + "/", methods=HTTP_METHODS)
        def wiz_index_handler(*args, **kwargs):
            wiz.response.status(404)

        # app's api request path
        @app.route(wizurl + "/api", methods=HTTP_METHODS)
        @app.route(wizurl + "/api/", methods=HTTP_METHODS)
        @app.route(wizurl + "/api/<path:path>", methods=HTTP_METHODS)
        def wiz_api_handler(*args, **kwargs):
            try:
                segment = wiz.match(f"{wizurl}/api/<app_id>/<fnname>/<path:path>")
                if segment is not None:
                    app_id = segment.app_id
                    fnname = segment.fnname
                    wiz.request.segment = segment

                    app = wiz.app(app_id)
                    apifn = app.api()

                    if apifn is None: wiz.response.status(404)
                    if fnname not in apifn: wiz.response.status(404)

                    if '__startup__' in apifn:
                        season.util.fn.call(apifn['__startup__'], wiz=wiz)

                    season.util.fn.call(apifn[fnname], wiz=wiz)
            except season.exception.ResponseException as e:
                raise e
            except Exception as e:
                wiz.tracer.error = traceback.format_exc()
                raise season.exception.ErrorException()
            
            wiz.response.status(404)

        # plugin resources request path
        @app.route(wizurl + "/resources", methods=HTTP_METHODS)
        @app.route(wizurl + "/resources/", methods=HTTP_METHODS)
        @app.route(wizurl + "/resources/<path:path>", methods=HTTP_METHODS)
        def wiz_resource_handler(*args, **kwargs):
            try:
                segment = wiz.match(f"{wizurl}/resources/<plugin_id>/<path:path>")
                plugin_id = segment.plugin_id
                path = segment.path
                filepath = os.path.join(season.path.project, "plugin", plugin_id, "resources", path)
                if os.path.isfile(filepath):
                    dirname = os.path.dirname(filepath)
                    filename = os.path.basename(filepath)
                    response = wiz.server.flask.send_from_directory(dirname, filename)
                    raise season.exception.ResponseException(200, response)
                wiz.response.abort(404)
            except season.exception.ResponseException as e:
                raise e
            except HTTPException as e:
                raise e
            except Exception as e:
                wiz.tracer.error = traceback.format_exc()
                raise season.exception.ErrorException()
            
        # TODO: plugin request path
        @app.route(wizurl + "/ui/<path:path>", methods=HTTP_METHODS)
        def wiz_plugin_handler(*args, **kwargs):
            try:
                segment = wiz.match(f"{wizurl}/ui/<plugin_id>/<path:path>")
                if segment is not None:
                    plugin_id = segment.plugin_id
                    wiz.request.segment = segment
                    print(plugin_id)

                wiz.response.status(404)
            except season.exception.ResponseException as e:
                raise e
            except Exception as e:
                wiz.tracer.error = traceback.format_exc()
                raise season.exception.ErrorException()
            
            wiz.response.abort(404)
