import os
import traceback
import time
import logging

import flask
import flask_socketio

import season
from season.core.lib.server.http import HTTP
from season.core.lib.server.config import Config

class Server:

    def __init__(self):
        self.boottime = time.time()

        # load config
        self.config = season.util.std.stdClass()
        self.load_config()
        config = self.config

        # create flask server & set env
        app = flask.Flask('__main__', static_url_path='')

        log = logging.getLogger('werkzeug')
        log.disabled = True
        app.logger.disabled = True
        os.environ["WERKZEUG_RUN_MAIN"] = "true"

        app.jinja_env.variable_start_string = config.server.jinja_variable_start_string
        app.jinja_env.variable_end_string = config.server.jinja_variable_end_string
        app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')

        # create socketio server
        sioconfig = config.socketio.get("app", dict())
        socketio = flask_socketio.SocketIO(app, **sioconfig)

        # set server
        self.app = app
        self.socketio = socketio
        self.flask = flask
        self.flask_socketio = flask_socketio

        # create wiz instance
        self.wiz = season.wiz(self)
        self.plugin = season.plugin(self)

        # http events
        http = HTTP(self)
    
    def load_config(self):
        self.config.server = Config.load("server")
        self.config.wiz = Config.load("wiz")
        self.config.socketio = Config.load("socketio")

    def run(self):
        config = self.config
        sioconfig = config.socketio.run
        sioconfig['host'] = config.server.http_host
        sioconfig['port'] = config.server.http_port

        socketio = self.socketio
        app = self.app

        socketio.run(app, **sioconfig)
