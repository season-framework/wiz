import os

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

class lib(stdClass):
    def __init__(self, framework):
        self.framework = framework
        self._cache = stdClass()

    def __getattr__(self, attr):
        if attr in self._cache:
            return self._cache[attr]

        libpath = os.path.join(self.framework.core.PATH.MODULES, self.framework.modulename,'lib', attr + '.py')
        if os.path.isfile(libpath):
            f = open(libpath, 'r')
            _code = f.read()
            f.close()

            _tmp = stdClass()
            exec(_code, _tmp)
            obj = _tmp
            self._cache[attr] = obj
            return obj

        libpath = os.path.join(self.framework.core.PATH.APP, 'lib', attr + '.py')
        if os.path.isfile(libpath):
            f = open(libpath, 'r')
            _code = f.read()
            f.close()

            _tmp = stdClass()
            exec(_code, _tmp)
            obj = _tmp
            self._cache[attr] = obj
            return obj

        if hasattr(core, attr):
            fn = getattr(core, attr)
            obj = fn(self.framework)
            self._cache[attr] = obj
            return obj
        
        return stdClass()

class core(stdClass):
    class session:
        def __init__(self, framework):
            self.framework = framework
            self.flask = framework.flask

        def has(self, key):
            if key in self.flask.seasion:
                return True
            return False
        
        def delete(self, key):
            self.flask.session.pop(key)

        def set(self, key, value):
            self.flask.session[key] = value

        def get(self, key, default=None):
            if key in self.flask.session:
                return self.flask.session[key]
            return default

        def clear(self):
            self.flask.session.clear()

        def to_dict(self):
            return dict(self.flask.session)
