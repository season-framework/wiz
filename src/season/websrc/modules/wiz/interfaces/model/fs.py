import os
import pickle
import json
import datetime
import shutil
import season
import mimetypes

class stdClass(dict):
    def __init__(self, *args, **kwargs):
        super(stdClass, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(stdClass, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(stdClass, self).__delitem__(key)
        del self.__dict__[key]
        
class Model:
    def __init__(self, framework):
        self.framework = framework
        self.config = season.stdClass()
        self.config.path = season.core.PATH.WIZ.CORE
        self.namespace = ""
        
    def basepath(self):
        first_ns = self.namespace.split("/")[0]
        if first_ns == 'wiz':
            namespace = "/".join(self.namespace.split("/")[1:])
            return os.path.join(season.core.PATH.PROJECT, namespace)
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

    def set_path(self, path):
        self.config.path = path
        return self

    def use(self, namespace):
        self.namespace = namespace
        fs = Model()
        fs.namespace = namespace
        return fs

    def list(self):
        return self.files()

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

    def isfile(self, filepath):
        return os.path.isfile(self.abspath(filepath))
    
    def isdir(self, filepath):
        return os.path.isdir(self.abspath(filepath))

    def copy(self, filepath1, filepath2):
        filepath1 = self.abspath(filepath1)
        filepath2 = self.abspath(filepath2)
        if os.path.isfile(filepath1):
            shutil.copy(filepath1, filepath2)
        else:
            shutil.copytree(filepath1, filepath2)

    def abspath(self, filepath=""):
        target_path = os.path.join(self.basepath(), filepath)
        notallowed = ["", "/"]
        if target_path in notallowed: 
            raise Exception("not allowed path")
        return target_path

    def makedirs(self, path):
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

    # file write
    def write(self, filepath, data):
        self.write_text(filepath, data)

    def write_text(self, filepath, data):
        abspath = self.abspath(filepath)
        self.__makedirs__(abspath)
        f = open(abspath, 'w')
        f.write(data)
        f.close()

    def write_json(self, filepath, obj):
        def json_default(value):
            if isinstance(value, datetime.date): 
                return value.strftime('%Y-%m-%d %H:%M:%S')
            return value

        obj = json.dumps(obj, default=json_default)
        abspath = self.abspath(filepath)
        self.__makedirs__(abspath)
        f = open(abspath, 'w')
        f.write(obj)
        f.close() 

    def write_file(self, filepath, file):
        abspath = self.abspath(filepath)
        self.__makedirs__(abspath)
        file.save(abspath)

    def write_pickle(self, filepath, data):
        abspath = self.abspath(filepath)
        self.__makedirs__(abspath)
        f = open(abspath, 'wb')
        pickle.dump(data, f)
        f.close()

    # file read
    def read(self, filepath):
        return self.read_text(filepath)

    def read_text(self, filepath):
        abspath = self.abspath(filepath)
        f = open(abspath, 'r')
        data = f.read()
        f.close()
        return data

    def read_json(self, filepath):
        abspath = self.abspath(filepath)
        f = open(abspath, 'r')
        data = f.read()
        f.close()
        data = self.__json__(data)
        return data

    def read_pickle(self, filepath):
        abspath = self.abspath(filepath)
        f = open(abspath, 'rb')
        data = pickle.load(f)
        f.close()
        return data

    # remove file
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
