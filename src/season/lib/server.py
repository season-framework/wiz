import time
import logging
import season

class Server:
    def __init__(self, path=None):
        self.boottime = time.time()
        self.package = season.lib.static.Package()
        self.path = season.lib.static.Path(path)
        self.config = season.lib.static.Config(server=self)
        
        self.cache = season.util.Cache() # system cache
        
        logging.getLogger('werkzeug').disabled = True

        # create app server & set env
        self.app = season.util.stdClass()
        self.app.flask = self.package.flask.Flask(self.config.boot.import_name, **self.config.boot.flask)
        self.app.flask.logger.disabled = True
        self.app.flask.secret_key = self.config.boot.secret_key
        self.app.socketio = self.package.socketio.SocketIO(self.app.flask, **self.config.boot.socketio)

        # build server on config
        season.util.compiler(self.config.boot.bootstrap).call(app=self.app, config=self.config)
        
        # bind events http / socketio
        season.lib.binding.http(self)
        season.lib.binding.socket(self)

    def run(self, **kwargs):
        config = self.config
        socketio = self.app.socketio
        app = self.app.flask

        for key in kwargs:
            if key in ['host', 'port', 'debug']:
                config.boot.run[key] = kwargs[key]
            else:
                config.boot[key] = kwargs[key]

        app.name = config.boot.import_name

        logger = season.util.Logger("boot", level=config.boot.log_level, trigger=print)
        logger.dev(f"server is running on... http://{config.boot.run.host}:{config.boot.run.port}")

        socketio.run(app, **config.boot.run)

    def wiz(self):
        try:
            if self.package.flask.g.wiz is not None:
                return self.package.flask.g.wiz
        except:
            pass
        
        wiz = season.lib.core.Wiz(self)

        try:
            self.package.flask.g.wiz = wiz
        except:
            pass

        return wiz
