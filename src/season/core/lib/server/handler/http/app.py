import os
import season
from werkzeug.exceptions import HTTPException
from season.core.lib.server.handler.http.base import Base

class Router(Base):
    def route(self, wiz, app, config):
        server = wiz.server
        HTTP_METHODS = config.server.http_method

        @app.route("/", methods=HTTP_METHODS)
        @app.route("/<string:module>", methods=HTTP_METHODS)
        @app.route("/<string:module>/", methods=HTTP_METHODS)
        @app.route("/<string:module>/<path:path>", methods=HTTP_METHODS)
        def request_handler(*args, **kwargs):
            wiz = season.wiz(server)
            try:
                wiz.trace()
                wiz.installed()
                path = wiz.request.uri()
                app, segment = wiz.route.match(path)

                if app is not None:
                    wiz.request.segment = season.stdClass(**segment)
                    app.proceed()

                wiz.response.abort(404)
            except season.exception.ResponseException as e:
                e.wiz = wiz
                raise e
            except HTTPException as e:
                e.wiz = wiz
                raise e
            except Exception as e:
                e.wiz = wiz
                raise e

class Resources(Base):
    def route(self, wiz, app, config):
        server = wiz.server

        @app.route('/resources')
        @app.route('/resources/')
        @app.route('/resources/<path:path>')
        def resources_handler(*args, **kwargs):
            wiz = season.wiz(server)
            try:
                wiz.trace()
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
                    if wiz.server.config.wiz.build_resource is not None:
                        res = season.util.fn.call(wiz.server.config.wiz.build_resource, wiz=wiz, resource_dirpath=dirname, resource_filepath=filename)
                        if res is not None: return res

                    response = wiz.server.flask.send_from_directory(dirname, filename)
                    raise season.exception.ResponseException(200, response)

                wiz.response.abort(404)
            except season.exception.ResponseException as e:
                e.wiz = wiz
                raise e
            except HTTPException as e:
                e.wiz = wiz
                raise e
            except Exception as e:
                e.wiz = wiz
                raise e

