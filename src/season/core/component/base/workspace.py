import season
import os
import datetime
import subprocess
from abc import *

def localized(fn):
    def wrapper_function(self, *args, **kwargs):
        if self.id is None:
            raise Exception("Not Localized Instance")
        return fn(self, *args, **kwargs)
    return wrapper_function
    
class App:
    def __init__(self, workspace):
        self.workspace = workspace
        self.wiz = workspace.wiz
        self.id  = None

    @abstractmethod
    def list(self):
        pass

    def is_instance(self):
        return self.id is not None

    @abstractmethod
    def __call__(self, app_id):
        pass

    # localized functions: app id required
    @localized
    def build(self):
        filepath = None
        if self.is_instance():
            filepath = self.fs().abspath()
        self.workspace.build(filepath)

    @abstractmethod
    def data(self, code=True):
        pass

    @abstractmethod
    def before_update(self, data):
        pass

    @abstractmethod
    def do_update(self, data):
        pass

    @localized
    def update(self, data):
        for key in data:
            if type(data[key]) == str:
                data[key] = data[key].replace('', '')
        
        data = self.before_update(data)
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 'created' not in data['package']:
            data['package']['created'] = timestamp

        fs = self.fs()
        fs.write.json("app.json", data['package'])

        self.do_update()

        if 'dic' in data:
            if fs.isdir("dic"):
                fs.delete("dic")
            fs.makedirs("dic")

            dicdata = data['dic']
            for lang in dicdata:
                val = dicdata[lang]
                lang = lang.lower()
                fs.write(os.path.join("dic", lang + ".json"), val)

        self.build()

    @abstractmethod
    def fs(self, *args):
        pass

    @localized
    def dic(self, lang=None):
        APP_ID = self.id
        wiz = self.wiz
        fs = self.fs("dic")

        if lang is None:
            lang = wiz.request.language()
            lang = lang.lower()
        
        data = fs.read.json(f'{lang}.json', None)
        if data is None:
            data = fs.read.json("default.json", dict())
        
        class Loader:
            def __init__(self, dicdata):
                self.dicdata = dicdata

            def __call__(self, key=None):
                dicdata = self.dicdata
                if key is None: 
                    return season.util.std.stdClass(dicdata)
                
                key = key.split(".")
                tmp = dicdata
                for k in key:
                    if k not in tmp:
                        return ""
                    tmp = tmp[k]
                return tmp

        return Loader(data)

    @localized
    def api(self):
        APP_ID = self.id
        wiz = self.wiz
        app = self.data()

        if app is None or 'api' not in app:
            return None

        code = app['api']
        if len(code) == 0:
            return None

        tag = wiz.mode()
        logger = wiz.logger(f"[{tag}/app/{APP_ID}/api]")
        dic = self.dic()

        ctrl = None
        if 'controller' in app['package'] and len(app['package']['controller']) > 0:
            ctrl = app['package']['controller']
            ctrl = wiz.controller(ctrl)()

        name = self.fs().abspath("api.py")
        apifn = season.util.os.compiler(code, name=name, logger=logger, controller=ctrl, dic=dic, wiz=wiz)
        
        return apifn

    @localized
    def delete(self):
        self.fs().delete()
        self.build()

class Workspace(metaclass=ABCMeta):
    def __init__(self, wiz):
        self.wiz = wiz

    @abstractmethod
    def path(self, *args):
        pass

    @abstractmethod
    def controller(self, *args, **kwargs):
        pass

    @abstractmethod
    def model(self, *args, **kwargs):
        pass

    def fs(self, *args):
        return season.util.os.FileSystem(self.path(*args))
