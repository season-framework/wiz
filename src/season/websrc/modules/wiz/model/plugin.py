import season
import base64
import json
import os
import datetime
from werkzeug.routing import Map, Rule
import time
import markupsafe
import git
import io

def addtabs(v, size=1):
    for i in range(size):
        v =  "    " + "\n    ".join(v.split("\n"))
    return v

def spawner(code, namespace, logger, **kwargs):
    fn = {'__file__': namespace, '__name__': namespace, 'print': logger}
    for key in kwargs: fn[key] = kwargs[key]
    exec(compile(code, namespace, 'exec'), fn)
    return fn

class Plugin(season.stdClass):
    def __init__(self, framework, pluginname):        
        self.__config__ = dict()
        
        self.flask = framework.flask
        self.flask_socketio = framework.flask_socketio
        self.socketio = framework.socketio
        self.lib = framework.lib
        self.model = framework.model
        self.wiz = framework.wiz
        self.request = framework.request
        self.response = framework.response
        self.PATH = framework.core.PATH

        self.__logger__ = self.logger("plugin")

    def logger(self, tag=None, log_color=94):
        class logger:
            def __init__(self, tag, log_color, wiz):
                self.tag = tag
                self.log_color = log_color
                self.wiz = wiz

            def log(self, *args):
                tag = self.tag
                log_color = self.log_color
                wiz = self.wiz
                
                if tag is None: tag = "undefined"
                tag = "[wiz]" + tag
                
                args = list(args)
                for i in range(len(args)): 
                    args[i] = str(args[i])
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                logdata = f"\033[{log_color}m[{timestamp}]{tag}\033[0m " + " ".join(args)
                print(logdata)

                wiz.socketio.emit("debug", logdata + "\n", namespace="/wiz", broadcast=True)
                
        return logger(tag, log_color, self).log

    def __dic__(self, app_id):
        class dic:
            def __init__(self, wizinst, app_id):
                self.__wizinst__ = wizinst
                self.mode = mode 
                self.app_id = app_id
                self.cache = dict()
            
            def dic(self, key=None):
                wiz = self.__wizinst__.__wiz__

                if mode is None or app_id is None:
                    return ""

                language = self.__wizinst__.request.language()
                language = language.lower()
                
                if language in self.cache:
                    dic = self.cache[language]
                else:
                    inst = wiz.cls.plugin(wiz)
                    dic = inst.dic(app_id)

                    if language in dic: dic = dic[language]
                    if "default" in dic: dic = dic["default"]
                    self.cache[language] = dic

                if key is None:
                    return dic

                key = key.split(".")
                tmp = dic
                for k in key:
                    if k not in tmp:
                        return ""
                    tmp = tmp[k]

                return tmp

        dicinst = dic(self, app_id)
        return dicinst.dic

    def __compiler__(self, codelang, code, **kwargs):
        logger = self.logger(f"[compiler][{codelang}]")
        try:
            if code is None: return ""
            if len(code) == 0: return code
            wiz = self.__wiz__
            fs = wiz.framework.model("wizfs", module="wiz").use(f"modules/wiz/compiler")
            if fs.isfile(f"{codelang}.py") == False:
                return code
            compiler = fs.read(f"{codelang}.py")
            compiler = spawner(compiler, "season.wiz.plugin.compiler", logger)
            return compiler['compile'](self, code, kwargs)
        except Exception as e:
            logger(e)
            raise e

class Model:
    def __init__(self, framework):
        self.framework = framework
        self.fs = framework.model("wizfs", module="wiz").use("wiz/plugin")

    def list(self):
        fs = self.fs
        plugins = fs.files()
        res = []
        for plugin_id in plugins:
            try:
                plugin_file = os.path.join(plugin_id, "plugin.wiz")
                if fs.isfile(plugin_file):
                    plugin_info = fs.read_json(plugin_file)
                    plugin_info['id'] = plugin_id
                    res.append(plugin_info)
            except:
                pass
        return res

    def get(self, plugin_id):
        fs = self.fs
        info_file = os.path.join(plugin_id, "plugin.wiz")
        route_file = os.path.join(plugin_id, "route.wiz")
        apps_file = os.path.join(plugin_id, "apps.wiz")

        res = dict()
        try:
            res['info'] = fs.read_json(info_file)
            res['info']['id'] = plugin_id
        except: 
            return None

        try:
            res['route'] = fs.read_json(route_file)
        except: 
            res['route'] = dict()
            res['route']['controller'] = ""
            res['route']['socketio'] = ""

        try:
            res['apps'] = fs.read_json(apps_file)
        except: 
            res['apps'] = []

        return res

    def instance(self, name):
        return Plugin(self, name)