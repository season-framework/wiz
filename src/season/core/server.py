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
        config = Config()
        self.config = config
        
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

        if config.server.build is not None:
            res = season.util.fn.call(config.server.build, app=app, socketio=socketio)
            if res is not None:
                self.app = app

        # set server
        self.app = app
        self.socketio = socketio
        self.flask = flask
        self.flask_socketio = flask_socketio

        # create wiz instance
        self.wiz = season.wiz(self)      
        self.plugin = season.plugin(self)
        self.wiz.plugin = self.plugin
        config.set(wiz=self.wiz)
        
        # http events
        HTTP(self)



    def run(self):
        config = self.config
        sioconfig = config.socketio.run
        sioconfig['host'] = config.server.http_host
        sioconfig['port'] = config.server.http_port

        socketio = self.socketio
        app = self.app

        socketio.run(app, **sioconfig)
