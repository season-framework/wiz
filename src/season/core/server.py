import os
import traceback
import time
import logging

import flask
import flask_socketio

import season
from season.core.lib.server.http import HTTP
from season.core.lib.server.socketio import SocketIO
from season.core.lib.server.config import Config

class Server:

    def __init__(self):
        self.boottime = time.time()

        # load config
        config = Config()
        self.config = config
        
        # create flask server & set env
        wsgi_flask = flask.Flask('__main__', static_url_path='')
        log = logging.getLogger('werkzeug')
        log.disabled = True
        wsgi_flask.logger.disabled = True
        os.environ["WERKZEUG_RUN_MAIN"] = "true"
        wsgi_flask.secret_key = config.server.secret_key
        wsgi_flask.jinja_env.variable_start_string = config.server.jinja_variable_start_string
        wsgi_flask.jinja_env.variable_end_string = config.server.jinja_variable_end_string
        wsgi_flask.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')

        # create socketio server
        sioconfig = config.socketio.get("app", dict())
        wsgi_socketio = flask_socketio.SocketIO(wsgi_flask, **sioconfig)

        # set wsgi server
        self.wsgi = season.stdClass()
        self.wsgi.flask = wsgi_flask
        self.wsgi.socketio = wsgi_socketio

        # build server on config
        if config.server.build is not None:
            season.util.fn.call(config.server.build, wsgi=self.wsgi)

        # set server libs
        self.flask = flask
        self.flask_socketio = flask_socketio

        # create wiz instance
        self.wiz = season.wiz(self)
        self.plugin = season.plugin(self)
        self.wiz.plugin = self.plugin
        config.set(wiz=self.wiz)
        
        # bind events
        HTTP(self)
        self.socket = SocketIO(self)

    def run(self):
        config = self.config
        sioconfig = config.socketio.run
        host = sioconfig['host'] = config.server.http_host
        port = sioconfig['port'] = config.server.http_port

        socketio = self.wsgi.socketio
        app = self.wsgi.flask

        print(f"wiz server is running on... http://{host}:{port}")
        socketio.run(app, **sioconfig)
