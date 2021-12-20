import time
boottime = round(time.time() * 1000)

import os
import datetime
import shutil
import json

from .version import VERSION_STRING as VERSION
from .util.stdclass import stdClass
from .framework.request import request
from .framework.segment import segment
from .framework.response import response
from .framework.lib import lib
from .framework.status import status

LOG_DEBUG = 0
LOG_INFO = 1
LOG_DEV = 2
LOG_WARNING = 3
LOG_ERROR = 4
LOG_CRITICAL = 5

version = __version__ = __VERSION__ = VERSION

core = stdClass()
core.PATH = stdClass()
core.PATH.FRAMEWORK = os.path.dirname(__file__)
core.PATH.PROJECT = os.path.join(os.getcwd())

# WIZ PATH
core.PATH.WIZ = stdClass()
core.PATH.WIZ.CORE = os.path.join(core.PATH.FRAMEWORK, 'websrc')
core.PATH.WIZ.CONFIG = os.path.join(core.PATH.PROJECT, 'wiz.json')

core.PATH.PUBLIC = os.path.join(core.PATH.PROJECT, 'public')
core.PATH.TEMPLATE = os.path.join(core.PATH.PUBLIC, 'templates')

# DEFAULT FRAMEWORK PATH
core.PATH.WEBSRC = os.path.join(core.PATH.PROJECT, 'websrc')
core.PATH.APP = os.path.join(core.PATH.WEBSRC, 'app')
core.PATH.MODULES = os.path.join(core.PATH.WEBSRC, 'modules')

# select framework mode
FRAMEWORK_MODE = 'lib'
if os.path.isfile(core.PATH.WIZ.CONFIG): FRAMEWORK_MODE = 'wiz'
elif os.path.isdir(core.PATH.WEBSRC): FRAMEWORK_MODE = 'web'

# if framework is wiz, use websrc as library path
if FRAMEWORK_MODE == 'wiz':
    core.PATH.PROJECT = os.path.join(os.getcwd())
    core.PATH.WEBSRC = core.PATH.WIZ.CORE
    core.PATH.APP = os.path.join(core.PATH.WEBSRC, 'app')
    core.PATH.MODULES = os.path.join(core.PATH.WEBSRC, 'modules')

# Framework Methods
core.CLASS = stdClass()
core.CLASS.REQUEST = request
core.CLASS.SEGMENT = segment
core.CLASS.RESPONSE = response
core.CLASS.LIB = lib
core.CLASS.RESPONSE.STATUS = status

interfaces = stdClass()
cache = stdClass()
cache.config = stdClass()

class Framework(stdClass):
    def __init__(self, **kwargs):
        season = kwargs['season']
        module = kwargs['module']
        module_path = kwargs['module_path']
        controller_path = kwargs['controller_path']
        segment_path = kwargs['segment_path']
        ERROR_INFO = kwargs['ERROR_INFO']
        _logger = kwargs['logger']
        flask = kwargs['flask']
        socketio = kwargs['socketio']
        flask_socketio = kwargs['flask_socketio']

        if 'starttime' in kwargs: self.starttime = kwargs['starttime']
        else: self.starttime = round(time.time() * 1000)

        self.modulename = ERROR_INFO.module = module
        self.modulepath = ERROR_INFO.modulepath = module_path
        self.controllerpath = ERROR_INFO.controllerpath = controller_path
        self.segmentpath = ERROR_INFO.segmentpath = segment_path

        self._cache = stdClass()
        self._cache.model = stdClass()
        self.flask = flask
        self.socketio = socketio
        self.flask_socketio = flask_socketio
        
        self.cache = season.cache

        self.core = season.core
        self.config = season.config
        self.request = season.core.CLASS.REQUEST(self)
        self.request.segment = season.core.CLASS.SEGMENT(self)
        self.response = season.core.CLASS.RESPONSE(self)
        self.lib = season.core.CLASS.LIB(self)

        self.dic = season.dic
        self.dic.set_language(self.request.language())

        def dic(namespaces):
            namespaces = namespaces.split(".")
            tmp = self.dic
            for ns in namespaces:
                if tmp[ns] is not None:
                    tmp = tmp[ns]
            return str(tmp)

        self.response.data.set(module=module, dic=dic)

        def log(*args):
            _logger(2, ERROR_INFO=ERROR_INFO, code=200, message=" ".join(map(str, args)))
        self.log = log

        def model(modelname, module=None):
            if module is None: module = self.modulename
            model_path = None
            if module is not None:
                model_path = os.path.join(season.core.PATH.MODULES, module, 'model', modelname + '.py')

                if os.path.isfile(model_path) == False:
                    model_path = os.path.join(season.core.PATH.APP, 'model', modelname + '.py')
            else:
                model_path = os.path.join(season.core.PATH.APP, 'model', modelname + '.py')

            if model_path in self._cache.model:
                return self._cache.model[model_path]
            
            if os.path.isfile(model_path) == False:
                self.response.error(500, 'Model Not Found')

            with open(model_path, mode="rb") as file:
                _code = file.read().decode('utf-8')
                _tmp = {'__file__': model_path}
                exec(compile(_code, model_path, 'exec'), _tmp)
                self._cache.model[model_path] = _tmp['Model'](self)
                return self._cache.model[model_path]

        self.model = model

core.CLASS.FRAMEWORK = Framework

class config(stdClass):
    def __init__(self, name='config', data=stdClass()):
        self.data = data
        self.name = name

    @classmethod
    def load(self, name='config'):
        if name in cache.config:
            return cache.config[name]
        c = config()

        # wiz support custom config, this just working as running web server
        if FRAMEWORK_MODE == 'wiz': 
            config_path = os.path.join(core.PATH.PROJECT, 'config', name + '.py')
        else: 
            config_path = os.path.join(core.PATH.APP, 'config', name + '.py')

        if os.path.isfile(config_path) == False:
            c.data = dict()

        try:
            with open(config_path, mode="rb") as file:
                _tmp = {'config': None}
                _code = file.read().decode('utf-8')
                exec(_code, _tmp)
                c.data = _tmp['config']
        except Exception as e:
            pass

        cache.config[name] = c
        return c

    def get(self, key=None, _default=None):
        if key is None:
            return self.data
        if key in self.data:
            return self.data[key]
        return _default

def build_template():
    if os.path.isdir(core.PATH.TEMPLATE):
        return

    try:
        shutil.rmtree(core.PATH.TEMPLATE)
    except:
        pass

    try:
        os.makedirs(core.PATH.TEMPLATE, exist_ok=True)
    except:
        pass

    def find_viewpath(directory):
        paths = []
        for (path, _, filenames) in os.walk(directory):
            viewpath = os.path.join(path, "view")
            if os.path.isdir(viewpath):
                paths.append(viewpath)
        return paths

    viewpaths = find_viewpath(core.PATH.MODULES)
    for viewpath in viewpaths:
        if os.path.isdir(viewpath) == False: continue
        module = viewpath[len(core.PATH.MODULES)+1:-5]
        targetpath = os.path.join(core.PATH.TEMPLATE, module)
        try:
            os.makedirs(os.path.dirname(targetpath), exist_ok=True)
        except:
            pass
        try:
            os.symlink(viewpath, targetpath)
        except:
            pass

core.build = stdClass()
core.build.template = build_template

# json_default
def json_default(value): 
    if isinstance(value, datetime.date): 
        return value.strftime('%Y-%m-%d %H:%M:%S') 
    raise str(value)

core.json_default = json_default    

# interfaces
class _interfaces(dict):
    def __init__(self, namespace="interfaces"):
        super(_interfaces, self).__init__()
        self.__NAMESPACE__ = namespace

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __getattr__(self, attr):
        NAMESPACE = ".".join([self.__NAMESPACE__, attr])
        FUNCNAME = NAMESPACE.split(".")[-1]

        def load_interface(FILEPATH):
            if os.path.isfile(FILEPATH):
                file = open(FILEPATH, mode="rb")
                _tmp = stdClass()
                _tmp['__file__'] = FILEPATH
                _code = file.read().decode('utf-8')
                file.close()
                exec(compile(_code, FILEPATH, 'exec'), _tmp)
                if FUNCNAME in _tmp:
                    return _tmp[FUNCNAME]
            return None

        # module interfaces
        path = NAMESPACE.split(".")[:-1]
        path = path[1:]
        for i in range(len(path)):
            idx = len(path) - i
            module = "/".join(path[:idx])
            module_path = os.path.join(core.PATH.MODULES, module)
            interface_path = "/".join(path[idx:]) + ".py"
            FILEPATH = os.path.join(module_path, "interfaces", interface_path)
            interface = load_interface(FILEPATH)
            if interface is not None: 
                return interface

        # global interfaces
        FILEPATH = os.path.join(core.PATH.APP, "/".join(NAMESPACE.split(".")[:-1])) + ".py"
        interface = load_interface(FILEPATH)
        if interface is not None: 
            return interface
    
        return _interfaces(NAMESPACE)

interfaces = _interfaces()

# core interfaces
class _interfacesc(dict):
    def __init__(self, namespace="interfaces"):
        super(_interfacesc, self).__init__()
        self.__NAMESPACE__ = namespace

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __getattr__(self, attr):
        NAMESPACE = ".".join([self.__NAMESPACE__, attr])
        FILEPATH = os.path.join(core.PATH.FRAMEWORK, 'framework', "/".join(NAMESPACE.split(".")[:-1])) + ".py"
        FUNCNAME = NAMESPACE.split(".")[-1]

        if os.path.isfile(FILEPATH):
            file = open(FILEPATH, mode="rb")
            _tmp = stdClass()
            _tmp['__file__'] = FILEPATH
            _code = file.read().decode('utf-8')
            file.close()
            exec(compile(_code, FILEPATH, 'exec'), _tmp)

            if FUNCNAME in _tmp:
                return _tmp[FUNCNAME]

        return _interfacesc(NAMESPACE)

core.interfaces = _interfacesc()

# dictionary
class dicObjClass(dict):
    def __init__(self, *args, **kwargs):
        super(dicObjClass, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        self[k] = dicObjClass(v)
                    else:
                        self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    self[k] = dicObjClass(v)
                else:
                    self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(dicObjClass, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(dicObjClass, self).__delitem__(key)
        del self.__dict__[key]

def __finddic__():
    mydict = stdClass()
    dicdir = os.path.join(core.PATH.APP, "dic")
    dicfile = os.path.join(dicdir, "default.json")

    # global dic
    if os.path.isfile(dicfile):
        try:
            filenames = os.listdir(dicdir)
            for filename in filenames:
                langname, ext = os.path.splitext(filename)
                if ext != ".json":
                    continue
                dicfile = os.path.join(dicdir, filename)
                if "__global__" not in mydict:
                    mydict.__global__ = dicObjClass()
                with open(dicfile) as data:
                    data = json.load(data)
                    data = stdClass(data)
                    mydict.__global__[langname.upper()] = data
        except: 
            pass

    # module dic
    for root, _, _ in os.walk(core.PATH.MODULES):
        dicdir = os.path.join(root, "dic")
        dicfile = os.path.join(dicdir, "default.json")

        if os.path.isfile(dicfile) == False:
            continue
        
        root = root.replace(core.PATH.MODULES + "/", "")
        ns = root.split('/')
        try:
            filenames = os.listdir(dicdir)
            for filename in filenames:
                langname, ext = os.path.splitext(filename)
                if ext != ".json":
                    continue
                dicfile = os.path.join(dicdir, filename)
                with open(dicfile) as data:
                    data = json.load(data)
                    data = stdClass(data)
                    tmp = mydict
                    for i in range(len(ns)):
                        n = ns[i]
                        if n not in tmp:
                            tmp[n] = dicObjClass()
                        if i == len(ns) - 1:    
                            tmp[n][langname.upper()] = data
                        tmp = tmp[n]
        except: 
            pass

    return mydict

class dicClass(dict):
    def __init__(self, root, obj=None, lang="DEFAULT", default_dic=None, default_dic_loc=[]):
        super(dicClass, self).__init__()
        self.obj = obj
        self.root = root
        self.lang = lang.upper()
        self.default_dic = default_dic
        self.default_dic_loc = default_dic_loc

    def set_language(self, lang):
        self.lang = lang.upper()

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __getattr__(self, attr):
        try:
            self.default_dic_loc.append(attr)

            # if attr in obj
            if attr in self.obj:
                obj = self.obj[attr]

                # if instance is dicObjClass, find language class
                if isinstance(obj, dicObjClass):
                    if "DEFAULT" in obj: 
                        self.default_dic = obj["DEFAULT"]
                        self.default_dic_loc = []
                    langobj = None
                    if self.lang in obj:
                        langobj = obj[self.lang]
                    elif "DEFAULT" in obj:
                        langobj = obj["DEFAULT"]
                    if langobj is not None:
                        return dicClass(self.root, langobj, self.lang, self.default_dic, self.default_dic_loc)
                
                if obj is not None:
                    return dicClass(self.root, obj, self.lang, self.default_dic, self.default_dic_loc)
            
            locs = self.default_dic_loc
            if self.default_dic is not None:
                langobj = self.default_dic
                for attr in locs:
                    if attr in langobj:
                        langobj = langobj[attr]
                    else:
                        langobj = None
                        break
                if langobj is not None:
                    return dicClass(self.root, langobj, self.lang, self.default_dic, self.default_dic_loc)

            #  if not in obj, return global dic
            if '__global__' in self.root:
                if self.lang in self.root.__global__:
                    obj = self.root.__global__[self.lang]
                    if attr in obj:
                        return dicClass(self.root, obj[attr], self.lang, self.default_dic, self.default_dic_loc)
                    
                if "DEFAULT" in self.root.__global__:
                    obj = self.root.__global__["DEFAULT"]
                    if attr in obj:
                        return dicClass(self.root, obj[attr], self.lang, self.default_dic, self.default_dic_loc)
        except:
            pass

        return dicClass(self.root, None, self.lang, self.default_dic, self.default_dic_loc)

    def __str__ (self):
        obj = self.obj
        if isinstance(obj, dicObjClass):
            if self.lang in obj:
                return str(obj[self.lang])
            if "DEFAULT" in obj:
                return str(obj["DEFAULT"])
            return "{}"
        return str(obj)


def bootstrap(*args, **kwargs):
    if 'ismain' in kwargs: ismain = kwargs['ismain']
    else: ismain = True

    if FRAMEWORK_MODE == 'web':
        from .util.bootstrap import bootstrap

        season = stdClass()
        season.FRAMEWORK_MODE = FRAMEWORK_MODE
        season.boottime = boottime
        season.core = core
        season.interfaces = interfaces
        season.config = config
        __DIC__ = __finddic__()
        season.dic = dicClass(__DIC__, __DIC__)
        season.cache = cache
        return bootstrap(season).bootstrap(ismain)

    elif FRAMEWORK_MODE == 'wiz':
        from .util.bootstrap_wiz import bootstrap_wiz

        season = stdClass()
        season.FRAMEWORK_MODE = FRAMEWORK_MODE
        season.boottime = boottime
        season.core = core
        season.interfaces = interfaces
        season.config = config
        __DIC__ = __finddic__()
        season.dic = dicClass(__DIC__, __DIC__)
        season.cache = cache
        return bootstrap_wiz(season).bootstrap(ismain)