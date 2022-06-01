import os
import traceback
from werkzeug.exceptions import HTTPException

import season
from season.core.lib.server.handler.http.base import Base

class Index(Base):
    def route(self, wiz, app, config):
        HTTP_METHODS = config.server.http_method
        wizurl = config.wiz.url
        if wizurl[-1] == "/": wizurl = wizurl[:-1]

        @app.route(wizurl, methods=HTTP_METHODS)
        @app.route(wizurl + "/", methods=HTTP_METHODS)
        def wiz_index_handler(*args, **kwargs):
            wiz.response.status(404)

class API(Base):
    def route(self, wiz, app, config):
        HTTP_METHODS = config.server.http_method
        wizurl = config.wiz.url
        if wizurl[-1] == "/": wizurl = wizurl[:-1]

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

class Resources(Base):
    def route(self, wiz, app, config):
        HTTP_METHODS = config.server.http_method
        wizurl = config.wiz.url
        if wizurl[-1] == "/": wizurl = wizurl[:-1]

        @app.route(wizurl + "/resources", methods=HTTP_METHODS)
        @app.route(wizurl + "/resources/", methods=HTTP_METHODS)
        @app.route(wizurl + "/resources/<path:path>", methods=HTTP_METHODS)
        def wiz_resource_handler(*args, **kwargs):
            try:
                plugin = wiz.server.plugin

                # find plugin resources
                segment = wiz.match(f"{wizurl}/resources/<plugin_id>/<path:path>")
                plugin_id = segment.plugin_id
                path = segment.path
                filepath = os.path.join(season.path.project, "plugin", 'modules', plugin_id, "resources", path)

                # if not exists, find default theme resources
                if os.path.isfile(filepath) == False:
                    segment = wiz.match(f"{wizurl}/resources/<path:path>")
                    path = segment.path
                    theme = plugin.config().theme
                    filepath = os.path.join(season.path.project, "plugin", 'themes', theme, "resources", path)

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

class Router(Base):
    def route(self, wiz, app, config):
        HTTP_METHODS = config.server.http_method
        wizurl = config.wiz.url
        if wizurl[-1] == "/": wizurl = wizurl[:-1]

        @app.route(wizurl + "/ui/<path:path>", methods=HTTP_METHODS)
        def wiz_plugin_handler(*args, **kwargs):
            try:
                segment = wiz.match(f"{wizurl}/ui/<plugin_id>/<path:path>")
                if segment is None: segment = wiz.match(f"{wizurl}/ui/<plugin_id>/")
                if segment is None: segment = wiz.match(f"{wizurl}/ui/<plugin_id>")

                if segment is not None:
                    plugin_id = segment.plugin_id
                    wiz.request.segment = segment

                    # set plugin
                    plugin = wiz.server.plugin.load(plugin_id)
                    plugin.trace()

                    # routing
                    path = plugin.request.uri()
                    if len(path) == 0: path = "/"
                    plugin.route.build()
                    app, segment = plugin.route.match(path)

                    if app is not None:
                        wiz.request.segment = season.stdClass(**segment)
                        app.proceed()
                    
                wiz.response.status(404)
            except season.exception.ResponseException as e:
                raise e
            except HTTPException as e:
                raise e
            except Exception as e:
                wiz.tracer.error = traceback.format_exc()
                raise season.exception.ErrorException()
            
            wiz.response.abort(404)
