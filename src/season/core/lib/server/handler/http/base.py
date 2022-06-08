from abc import *

class Base(metaclass=ABCMeta):
    def __init__(self, server):
        self.server = server
        wiz = server.wiz
        app = server.wsgi.flask
        config = server.config
        self.route(wiz, app, config)
    
    @abstractmethod
    def route(self, wiz, app, config):
        pass