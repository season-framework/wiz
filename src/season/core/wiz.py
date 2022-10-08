import os
import time
from werkzeug.routing import Map, Rule
import urllib
import traceback

import season
from season.core import component

class Branch:
    def __init__(self, wiz):
        self._wiz = wiz
        self._branch = None

        if wiz.request is not None:
            branch = wiz.request.cookies("season-wiz-branch", "main")
            if self.exists(branch):
                self._branch = branch

        if self._branch is None and self.exists('main'):
            self._branch = 'main'
        
        if self._branch is None and self.exists('master'):
            self._branch = 'master'

    def exists(self, branch):
        wiz = self._wiz
        server = wiz.server
        branchbasepath = server.path.branch
        branchpath = os.path.join(branchbasepath, branch)
        if os.path.isdir(branchpath):
            return True
        return False

    def list(self):
        server = self._wiz.server
        fs = season.util.os.FileSystem(server.path.branch)
        return fs.list()

    def path(self, *args):
        wiz = self._wiz
        server = wiz.server
        branchbasepath = server.path.branch
        branchpath = os.path.join(branchbasepath, self._branch, *args)
        return branchpath

    def checkout(self, branch):
        wiz = self._wiz
        server = wiz.server
        branchbasepath = server.path.branch
        branchpath = os.path.join(branchbasepath, branch)
        if os.path.isdir(branchpath):
            if wiz.response is not None:
                param = dict()
                param["season-wiz-branch"] = branch
                wiz.response.cookies.set(**param)
            self._branch = branch
        return self._branch

    def fs(self, *args):
        return season.util.os.FileSystem(self.path(*args))

    def __call__(self, branch=None):
        if branch is None:
            return self._branch
        branch = self.checkout(branch)
        return branch

class Mode:
    def __init__(self, wiz, mode):
        self._wiz = wiz
        self._mode = mode

        self._service = season.util.std.stdClass()
        self._service.request = component.service.Request(wiz)
        self._service.response = component.service.Response(wiz)

        self._ide = season.util.std.stdClass()
        self._ide.request = component.ide.Request(wiz)
        self._ide.response = component.ide.Response(wiz)

        self.change(mode)

    def __call__(self):
        return self._mode

    def change(self, mode):
        self._mode = mode
        target = None
        if mode == 'service': target = self._service
        elif mode == 'ide': target = self._ide

        self._wiz.request = target.request
        self._wiz.response = target.response

    def equal(self, mode):
        return self() == mode

class Uri:
    def __init__(self, wiz):
        self._wiz = wiz
        self._server = self._wiz.server

        baseurl = self._server.config.service.baseurl
        if len(baseurl) > 0 and baseurl[-1] == "/": baseurl = baseurl[:-1]
        wizurl = self._server.config.service.wizurl
        if len(wizurl) > 0 and wizurl[-1] == "/": wizurl = wizurl[:-1]
        asseturl = self._server.config.service.asseturl
        if len(asseturl) > 0 and asseturl[-1] == "/": asseturl = asseturl[:-1]

        self._base = baseurl
        self._wiz = wizurl
        self._asset = asseturl

    def _path(self, *args):
        paths = []
        for path in args:
            if len(path) > 0 and path[0] == "/": path = path[1:]
            paths.append(path)
        return "/".join(paths)

    def base(self, *args):
        if len(args) == 0:
            return self._base
        path = self._path(*args)
        return urllib.parse.urljoin(self._base + "/", path)

    def wiz(self, *args):
        if len(args) == 0: 
            return self._wiz
        path = self._path(*args)
        return urllib.parse.urljoin(self._wiz + "/", path)

    def ide(self, *args):
        base = self.wiz("ide")
        if len(args) == 0: 
            return base
        path = self._path(*args)
        return urllib.parse.urljoin(base + "/", path)

    def asset(self, *args):
        if len(args) == 0: return self._asset
        path = self._path(*args)
        return urllib.parse.urljoin(self._asset + "/", path)

    def __call__(self, *args):
        wiz = self._wiz
        if wiz.mode.equal("service"):
            return self.base(*args)
        return self.wiz(*args)

class Dev:
    def __init__(self, wiz):
        self._wiz = wiz
        try:
            is_dev = wiz.request.cookies("season-wiz-devmode", "false")
            if is_dev == "false":
                is_dev = False
            else: 
                is_dev = True

            branch = wiz.branch()
            if branch not in ['master', 'main']:
                is_dev = True
        except:
            is_dev = False
        self._status = is_dev        

    def set(self, DEVMODE):
        wiz = self._wiz
        if DEVMODE == False: DEVMODE = "false"
        elif DEVMODE == True: DEVMODE = "true"
        else: DEVMODE = "false"
        if DEVMODE == 'true': self._status = True
        else: self._status = False
        param = dict()
        param["season-wiz-devmode"] = DEVMODE
        wiz.response.cookies.set(**param)
        
    def __call__(self):
        return self._status

class Tracer:
    def __init__(self, wiz):
        self._wiz = wiz
        self.timestamp = time.time()
        self.code = None
        self.log = []
    
    def __call__(self):
        tag = ""
        if self.code is not None:
            tag = f"[{self.code}]{tag}"
        if self.timestamp is not None:
            timelabs = str(round((time.time() - self.timestamp) * 1000))
            tag = f"[{timelabs}ms]{tag}"
        return tag

class Logger:
    def __init__(self, wiz, tag=None):
        self.server = wiz.server
        self.wiz = wiz
        self.tag = tag

    def __call__(self, *args, level=3):
        server = self.server
        tag = self.tag
        wiz = self.wiz

        if level < server.config.service.log_level: return
        if tag is None: tag = ""
        if wiz.tracer is not None and wiz.onapp:
            tag = wiz.tracer() + tag

        tagmap = ['DEBUG', 'INFO_', 'WARN_', 'DEV__', 'ERROR', 'CRIT_']
        tagcolor = [94, 94, 93, 94, 91, 91]
        if level < len(tagmap): tag = "[" + tagmap[level] + "]" + tag
        color = tagcolor[level]

        args = list(args)
        for i in range(len(args)): 
            args[i] = str(args[i])
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        logdata = f"\033[{color}m[{timestamp}]{tag}\033[0m " + " ".join(args)

        if server.config.boot.log is not None:
            try:
                logpath = os.path.join(server.path.root, server.config.boot.log)
                if os.path.exists(logpath) == False:
                    f = open(logpath, "w")
                    f.write("")
                    f.close()
                f = open(logpath, "a")
                f.write(logdata + "\n")
                f.close()
            except:
                pass
        else:
            print(logdata)
    
        try:
            if wiz is not None and wiz.dev():
                branch = wiz.branch()
                server.app.socketio.emit("log", logdata + "\n", namespace=wiz.uri.ide(), to=branch, broadcast=True)
        except Exception as e:
            pass

class Config(season.util.std.stdClass):
    def __init__(self, wiz, **env):
        self.wiz = wiz
        env['wiz'] = wiz
        self.__env__ = env
        self.__cache__ = dict()

    def set(self, **env):
        for key in env:
            self.__env__[key] = env[key]

    def clean(self):
        self.__cache__ = dict()

    def __call__(self, name):
        return self.__getattr__(name)

    def __getattr__(self, name):
        if name in self.__cache__:
            return self.__cache__[name]

        class ConfigBase(season.util.std.stdClass):
            DEFAULT_VALUES = dict()

            def __init__(self, values=dict()):
                default = self.DEFAULT_VALUES
                for key in default:
                    _type, val = default[key]
                    if key not in values:
                        if _type is not None:
                            val = _type(val)
                        values[key] = val
                    else:
                        if _type is not None:
                            values[key] = _type(values[key])
                super(ConfigBase, self).__init__(values)
                
            def __getattr__(self, attr):
                val = super(ConfigBase, self).__getattr__(attr)
                if attr in self.DEFAULT_VALUES:
                    _type, _default = self.DEFAULT_VALUES[attr]
                    if val is None: val = _default
                    if _type is not None: val = _type(val)
                return val

        def build_config(base_config=dict()):
            config = ConfigBase(base_config)
            self.__cache__[name] = config
            return config

        wiz = self.wiz
        workspace = wiz.workspace()
        fs = workspace.fs("config")
        config_path = name + '.py'
        if fs.isfile(config_path) == False:
            return build_config()

        _code = fs.read(config_path, "")

        env = dict()
        env['__name__'] = config_path
        env['__file__'] = config_path

        logger = wiz.logger("[config/{name}]")
        env['print'] = logger
        env['display'] = logger

        try:
            exec(compile(_code, config_path, 'exec'), env)
        except Exception as e:
            if logger is not None:
                errormsg = f"error: config/{name}.py\n" + traceback.format_exc()
                logger(errormsg, level=season.LOG_CRITICAL)
        
        config = season.util.std.stdClass()
        for key in env:
            if key.startswith("__") and key.endswith("__"): continue
            config[key] = env[key]

        return build_config(config)

class Wiz(season.util.std.stdClass):
    def __init__(self, server, **kwargs):
        self.memory = season.util.std.stdClass()
        self.server = server
        self.branch = Branch(self)
        self.uri = Uri(self)
        self.config = Config(self)
        self.request = None
        self.response = None
        self.tracer = None
        self.mode = None
        self.onapp = False
                
    def workspace(self, mode=None):
        if self.mode is not None:
            if mode is None: 
                mode = self.mode()
        if mode is None: 
            mode = 'service'
        if mode == 'ide':
            return component.ide.Workspace(self)
        return component.service.Workspace(self)

    def model(self, namespace):
        return self.workspace().model(namespace)

    def controller(self, namespace):
        return self.workspace().controller(namespace)

    def logger(self, tag=None):
        return Logger(self, tag)

    def __call__(self, mode="service"):
        wiz = Wiz(self.server)
        try:
            wiz.tracer = Tracer(wiz)
        except:
            pass
        try:
            wiz.mode = Mode(wiz, mode)
        except:
            pass
        try:
            wiz.branch = Branch(wiz)
        except:
            pass
        try:
            wiz.dev = Dev(wiz)
        except:
            pass
        return wiz