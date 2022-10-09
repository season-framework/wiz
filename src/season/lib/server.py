import sys
import os
import traceback
import time
import logging

import flask
import flask_socketio

import season

class Server:
    def __init__(self, path=None):
        self.boottime = time.time()
        self._wiz = None

        # set server libs
        self.package = season.util.std.stdClass()
        self.package.flask = flask
        self.package.flask_socketio = flask_socketio

        self.path = season.util.std.stdClass()
        self.path.root = path
        if path is None: self.path.root = os.getcwd()
        self.path.config = os.path.join(self.path.root, "config")
        self.path.public = os.path.join(self.path.root, "public")
        self.path.ide = os.path.join(self.path.root, "ide")
        self.path.branch = os.path.join(self.path.root, "branch")

        # load config
        self.config = config = season.core.config(server=self)

        # create flask server & set env
        self.app = season.util.std.stdClass()
        self.app.flask = flask.Flask(config.boot.import_name, **config.boot.flask)
        self.app.flask.logger.disabled = True
        self.app.flask.secret_key = config.boot.secret_key

        _log = logging.getLogger('werkzeug')
        _log.disabled = True

        # create socketio server
        self.app.socketio = flask_socketio.SocketIO(self.app.flask, **config.boot.socketio)

        self._wiz = season.core.wiz(self)

        @self.app.flask.before_request
        def before_request():
            self.package.flask.g.wiz = None
            wiz = self.wiz()
            wiz.onapp = True
            season.util.fn.call(config.service.before_request, wiz=wiz)

        # build server on config
        season.util.fn.call(config.boot.bootstrap, app=self.app, config=config)
        
        # bind events http / socketio
        http = season.core.http(self)
        http.bind()

        self.socket = socket = season.core.socket(self)
        socket.bind()

    def flask(self):
        return self.package.flask

    def socketio(self):
        return self.package.flask_socketio

    def wiz(self):
        try:
            if self.package.flask.g.wiz is None:
                self.package.flask.g.wiz = self._wiz()
            return self.package.flask.g.wiz
        except:
            return self._wiz

    def run(self, host=None, port=None, log=None, **kwargs):
        config = self.config
        socketio = self.app.socketio
        app = self.app.flask

        if host is not None: config.boot.run.host = host
        if port is not None: config.boot.run.port = port
        if log is not None: config.boot.log = log

        for key in kwargs:
            config.boot[key] = kwargs[key]

        app.name = "__main__"

        logger = self.wiz().logger("[BOOT]")
        logger(f"server is running on... http://{config.boot.run.host}:{config.boot.run.port}", level=season.LOG_DEV)
        socketio.run(app, **config.boot.run)

    def wsgi(self):
        return self.app.flask