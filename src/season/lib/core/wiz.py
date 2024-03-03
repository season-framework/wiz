import os
import time
import season
from season.lib.core import struct

class Wiz:
    def __init__(self, server):
        self.server = server
        self.memory = season.util.stdClass()
        self.timestamp = time.time()
        
        self.uri = struct.Uri(self)
        self.response = struct.Response(self)
        self.request = struct.Request(self)
        self.project = struct.Project(self)
        self.config = struct.Config(self)
        self.ide = struct.IDE(self)

    def src(self, *args):
        return self.project.fs("bundle", "src", *args)
    
    def path(self, *args):
        return os.path.join(self.server.path.root, *args)

    def fs(self, *args):
        return season.util.filesystem(self.path(*args))
        
    def logger(self, *tags):
        ts = int((time.time() - self.timestamp) * 1000)
        if ts > 0:
            ts =  f"{ts}ms"
            tags = list(tags)
            tags = [ts] + tags
        return struct.Logger(self, *tags)

    def model(self, namespace):
        wiz = self
        fs = self.src("model")

        cachens = 'model.code#' + wiz.project()
        cache = wiz.server.cache.get(cachens, dict())

        if namespace in cache:
            code = cache[namespace]
        else:
            code = fs.read(f"{namespace}.py")
            code = compile(code, fs.abspath(namespace + ".py"), 'exec')
            cache[namespace] = code

        logger = wiz.logger(f"model/{namespace}")
        model = season.util.compiler().build(code, name=fs.abspath(namespace + ".py"), logger=logger, wiz=wiz).fn
        return model['Model']

    def controller(self, namespace):
        wiz = self
        fs = self.src("controller")

        cachens = 'controller.code#' + wiz.project()
        cache = wiz.server.cache.get(cachens, dict())

        if namespace in cache:
            code = cache[namespace]
        else:
            code = fs.read(f"{namespace}.py")
            code = compile(code, fs.abspath(namespace + ".py"), 'exec')
            cache[namespace] = code

        logger = wiz.logger(f"ctrl/{namespace}")
        ctrl = season.util.compiler().build(code, name=fs.abspath(namespace + ".py"), logger=logger, wiz=wiz).fn
        return ctrl['Controller']
