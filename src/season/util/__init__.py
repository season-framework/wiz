from season.util.filesystem import filesystem
fs = filesystem

from season.util.compiler import compiler
from season.util.decorator import decorator
from season.util import string
from season.util.logger import Logger
from season.util.cache import Cache

class stdClass(dict):
    def __init__(self, *args, **kwargs):
        super(stdClass, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        self[k] = stdClass(v)
                    else:
                        self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    self[k] = stdClass(v)
                else:
                    self[k] = v
    
    def __getitem__(self, attr):
        return self.__getattr__(attr)

    def __getattr__(self, attr):
        obj = self.get(attr)
        if type(obj) == dict:
            return stdClass(obj)
        return obj

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
