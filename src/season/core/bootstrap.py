import time
import os
import logging
import flask
import flask_socketio
from werkzeug.exceptions import HTTPException

import season

stdClass = season.util.std.stdClass

def bootstrap(*args, **kwargs):
    boottime = time.time()

    server = season.Server()
    server.run()
    
    # HTTP_METHODS = server.HTTP_METHODS

    # # request handler
    # @app.route("/", methods=HTTP_METHODS)
    # @app.route("/<string:module>", methods=HTTP_METHODS)
    # @app.route("/<string:module>/", methods=HTTP_METHODS)
    # @app.route("/<string:module>/<path:path>", methods=HTTP_METHODS)
    # def request_handler(*args, **kwargs):
    #     server.http.request()
    #     wiz.response.abort(404)

    
    # boottime = round(time.time() * 1000) - boottime

    # # start server
    # siorunconfig = config.socketio.get("run", dict())
    # siorunconfig['host'] = host
    # siorunconfig['port'] = port
    # socketio.run(app, **siorunconfig)