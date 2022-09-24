import datetime
import os
import json
import shutil
import mimetypes
import numpy as np
import pandas as pd
import pickle
import time
from PIL import Image

import season

def compiler(code, name=None, logger=print, **kwargs):
    fn = {'__file__': name, '__name__': name, 'print': logger, 'season': season}
    for key in kwargs: fn[key] = kwargs[key]
    exec(compile(code, name, 'exec'), fn)
    return fn

# function timer util
def timer(func):
    def decorator(*args, **kwargs):
        st = round(time.time() * 1000)
        func(*args, **kwargs)
        et = round(time.time() * 1000)
        print(f"[timelab]", et - st, "ms")
    return decorator

# file system util
class FileSystem:
    def __init__(self, basepath="."):
        self.config = season.util.std.stdClass()
        self.config.path = basepath
        self.namespace = ""

        DEFAULT_VALUE = "__ERROR__"

        class read:
            def __init__(self, parent):
                self.__parent__ = parent
                
                self.image = season.util.std.stdClass()
                self.image.PIL = self.image.pillow = self.__image_pil__
                self.image.numpy = self.image.np = self.__image_numpy__

            def __call__(self, filepath, default=DEFAULT_VALUE):
                return self.text(filepath, default=default)

            def text(self, filepath, default=DEFAULT_VALUE):
                try:
                    abspath = self.__parent__.abspath(filepath)
                    f = open(abspath, 'r')
                    data = f.read()
                    f.close()
                    return data
                except Exception as e:
                    if default == DEFAULT_VALUE:
                        raise e
                    return default

            def json(self, filepath, default=DEFAULT_VALUE):
                try:
                    abspath = self.__parent__.abspath(filepath)
                    f = open(abspath, 'r')
                    data = f.read()
                    f.close()
                    data = self.__parent__.__json__(data)
                    return data
                except Exception as e:
                    if default == DEFAULT_VALUE:
                        raise e
                    return default

            def pickle(self, filepath, default=DEFAULT_VALUE):
                try:
                    abspath = self.__parent__.abspath(filepath)
                    f = open(abspath, 'rb')
                    data = pickle.load(f)
                    f.close()
                    return data
                except Exception as e:
                    if default == DEFAULT_VALUE:
                        raise e
                    return default
            
            def __image_pil__(self, filepath, default=DEFAULT_VALUE):
                try:
                    abspath = self.__parent__.abspath(filepath)
                    return Image.open(abspath)
                except Exception as e:
                    if default == DEFAULT_VALUE:
                        raise e
                    return default

            def __image_numpy__(self, filepath, default=DEFAULT_VALUE):
                try:
                    img = self.__image_pil__(filepath)
                    return np.array(img)
                except Exception as e:
                    if default == DEFAULT_VALUE:
                        raise e
                    return default

            def csv(self, filepath, default=DEFAULT_VALUE):
                try:
                    abspath = self.__parent__.abspath(filepath)
                    df = pd.read_csv(abspath)
                    return df.to_numpy()
                except Exception as e:
                    if default == DEFAULT_VALUE:
                        raise e
                    return default

            def excel(self, filepath, default=DEFAULT_VALUE):
                try:
                    abspath = self.__parent__.abspath(filepath)
                    df = pd.read_excel(abspath)
                    return df.to_numpy()
                except Exception as e:
                    if default == DEFAULT_VALUE:
                        raise e
                    return default

        class write:
            def __init__(self, parent):
                self.__parent__ = parent

                self.image = season.util.std.stdClass()
                self.image.PIL = self.image.pillow = self.__image_pil__
                self.image.numpy = self.image.np = self.__image_numpy__

            def __call__(self, filepath, data):
                return self.text(filepath, data)

            def text(self, filepath, data):
                abspath = self.__parent__.abspath(filepath)
                self.__parent__.__makedirs__(abspath)
                f = open(abspath, 'w')
                f.write(data)
                f.close()

            def json(self, filepath, obj, default=None, indent=4):
                def json_default(value):
                    if isinstance(value, datetime.date): 
                        return value.strftime('%Y-%m-%d %H:%M:%S')
                    return value

                if default is None:
                    default = json_default

                obj = json.dumps(obj, default=default, indent=indent)
                abspath = self.__parent__.abspath(filepath)
                self.__parent__.__makedirs__(abspath)
                f = open(abspath, 'w')
                f.write(obj)
                f.close() 

            def file(self, filepath, file):
                abspath = self.__parent__.abspath(filepath)
                self.__parent__.__makedirs__(abspath)
                file.save(abspath)

            def pickle(self, filepath, data):
                abspath = self.__parent__.abspath(filepath)
                self.__parent__.__makedirs__(abspath)
                f = open(abspath, 'wb')
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
                f.close()

            def excel(self, filepath, data, columns=None, na_rep=''):
                abspath = self.__parent__.abspath(filepath)
                if columns is not None: data = pd.DataFrame(data, columns=columns)
                else: data = pd.DataFrame(data)
                data.to_excel(abspath, na_rep=na_rep)

            def csv(self, filepath, data, columns=None, sep=',', na_rep=''):
                abspath = self.__parent__.abspath(filepath)
                if columns is not None: data = pd.DataFrame(data, columns=columns)
                else: data = pd.DataFrame(data)
                data.to_csv(abspath, sep=sep, na_rep=na_rep)

            def __image_pil__(self, filepath, img):
                abspath = self.__parent__.abspath(filepath)
                self.__parent__.__makedirs__(abspath)
                img.save(abspath)

            def __image_numpy__(self, filepath, img):
                img = Image.fromarray(img)
                self.__image_pil__(filepath, img)

        self.read = read(self)
        self.write = write(self)
        
    def basepath(self):
        return os.path.join(self.config.path, self.namespace)

    def __json__(self, jsonstr):
        try:
            return json.loads(jsonstr)
        except:
            return None

    def __walkdir__(self, dirname):
        result = []
        for root, dirs, files in os.walk(dirname):
            for filename in files:
                if filename.startswith('.'): continue
                abspath = os.path.join(root, filename)
                result.append(abspath[len(self.basepath()):])
        return result

    def use(self, namespace):
        namespace = os.path.join(self.namespace, namespace)
        fs = FileSystem(self.config.path)
        fs.namespace = namespace
        return fs

    def set_path(self, path):
        self.config.path = path
        return self

    def cd(self, namespace):
        namespace = os.path.join(self.namespace, namespace)
        self.namespace = namespace
        return self

    def pwd(self):
        return self.abspath()

    def ls(self, filepath=""):
        return self.files(filepath=filepath)

    def list(self, filepath=""):
        return self.files(filepath=filepath)

    def files(self, filepath="", page=None, dump=20, recursive=False):
        try:
            abspath = self.abspath(filepath)
            if recursive == True:
                return self.__walkdir__(abspath)

            files = os.listdir(abspath)
            if page is None:
                return files
            page = (page - 1) * dump
            return files[page:page+dump]
        except:
            return []

    def count(self, filepath=""):
        try:
            abspath = self.abspath(filepath)
            return len(os.listdir(abspath))
        except:
            return 0

    def exists(self, filepath=""):
        if self.isfile(filepath):
            return True
        if self.isdir(filepath):
            return True
        return False

    def isfile(self, filepath=""):
        return os.path.isfile(self.abspath(filepath))
    
    def isdir(self, filepath=""):
        return os.path.isdir(self.abspath(filepath))

    def __copy__(self, src, dest, ignore=None):
        if os.path.isdir(src):
            if not os.path.isdir(dest):
                os.makedirs(dest)
            files = os.listdir(src)
            ignored = set()
            for f in files:
                if f not in ignored:
                    self.__copy__(os.path.join(src, f), os.path.join(dest, f), ignore)
        else:
            shutil.copyfile(src, dest)

    def copy(self, filepath1, filepath2):
        filepath1 = self.abspath(filepath1)
        filepath2 = self.abspath(filepath2)
        self.__copy__(filepath1, filepath2)

    def abspath(self, filepath=""):
        target_path = os.path.join(self.basepath(), filepath)
        notallowed = ["", "/"]
        if target_path in notallowed: 
            raise Exception("not allowed path")
        return os.path.realpath(target_path)

    def makedirs(self, path=""):
        try:
            path = self.abspath(path)
            os.makedirs(path)
        except:
            pass

    def __makedirs__(self, path):
        try:
            filedir = os.path.dirname(path)
            os.makedirs(filedir)
        except Exception as e:
            pass

    def mimetype(self, path):
        path = self.abspath(path)
        return mimetypes.guess_type(path)[0]

    def rename(self, path, rename):
        self.move(path, rename)

    def move(self, path, rename):
        path = self.abspath(path)
        rename = self.abspath(rename)
        shutil.move(path, rename)

    def remove(self, filepath=""):
        self.delete(filepath)

    def delete(self, filepath=""):
        abspath = self.abspath(filepath)
        try:
            shutil.rmtree(abspath)
        except Exception as e:
            try:
                os.remove(abspath)
            except Exception as e:
                return False
        return True
