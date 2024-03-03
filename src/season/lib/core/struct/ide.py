import os
import season
from .request import Request
from .idecomponent.build import Build

class _Request(Request):
    def uri(self):
        ideurl = self.wiz.uri.ide() + "/ide"
        return super().uri()[len(ideurl):]

class Plugin:
    def __init__(self, wiz, name=None):
        self.wiz = wiz
        self.name = name

    def __call__(self, name):
        return Plugin(self.wiz, name)

    def fs(self, *args):
        return self.wiz.fs("plugin", *args)
    
    def list(self):
        fs = self.fs()
        res = fs.ls()
        plugins = []
        for plugin in res:
            if fs.exists(f"{plugin}/plugin.json"):
                plugins.append(plugin)
        return plugins
    
    def model(self, namespace):
        wiz = self.wiz
        fs = self.fs(self.name, "model")

        cachens = 'ide.model.code'
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
    
    def command(self, namespace):
        wiz = self.wiz
        fs = self.fs(self.name)
        code = fs.read(f"command.py")
        code = compile(code, fs.abspath("command.py"), 'exec')
        logger = wiz.logger(self.name + "/command")
        command = season.util.compiler().build(code, name=fs.abspath("command.py"), logger=logger, wiz=wiz).fn
        return command[namespace]
    
class IDE:
    def __init__(self, wiz):
        self.wiz = wiz
        self.request = _Request(wiz)
        self.plugin = Plugin(wiz)
        self.build = Build(wiz)

    def fs(self, *args):
        return self.wiz.fs("ide", *args)

    def api(self, app_id):
        fs = self.fs("app", app_id)
        app = fs.read.json("app.json", None)
        app['api'] = fs.read("api.py", None)

        if app is None or app['api'] is None:
            return None
        
        code = app['api']
        if len(code) == 0:
            return None
        
        logger = self.wiz.logger(f"ide/app/{app_id}/api")
        name = fs.abspath("api.py")

        return season.util.compiler().build(code, name=name, logger=logger, wiz=self.wiz).fn
