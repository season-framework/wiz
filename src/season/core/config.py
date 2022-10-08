import os
import season
import traceback

stdClass = season.util.std.stdClass

class base(stdClass):
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
        super(base, self).__init__(values)
        
    def __getattr__(self, attr):
        val = super(base, self).__getattr__(attr)
        if attr in self.DEFAULT_VALUES:
            _type, _default = self.DEFAULT_VALUES[attr]
            if val is None: val = _default
            if _type is not None: val = _type(val)
        return val

class bootConfig(base):
    class socketioConfig(base):
        DEFAULT_VALUES = {
            'cors_allowed_origins': (str, '*'),
            'async_handlers': (bool, True),
            'always_connect': (bool, False),
            'manage_session': (bool, True)
        }

    class flaskConfig(base):
        pass

    class runConfig(base):
        DEFAULT_VALUES = {
            'host': (str, '0.0.0.0'),
            'port': (int, 3000),
            'debug': (None, None),
            'use_reloader': (bool, False)
        }

    DEFAULT_VALUES = {
        'python_executable': (None, None),
        'allowed_method': (list, ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']),
        'bootstrap': (None, season.util.fn.dummy),
        'dev': (bool, False),
        'flask': (flaskConfig, dict()),
        'import_name': (str, '__main__'),
        'log': (None, None),
        'run': (runConfig, dict()),
        'secret_key': (str, 'season-wiz-secret'),
        'socketio': (socketioConfig, dict())
    }

class serviceConfig(base):
    DEFAULT_VALUES = {
        'log_level': (int, 3),
        'title': (str, 'WIZ IDE'),
        'baseurl': (str, '/'),
        'asseturl': (str, '/assets'),
        'wizurl': (str, '/wiz'),
        'build_resource': (None, season.util.fn.dummy),
        'before_request': (None, season.util.fn.dummy),
        'after_request': (None, season.util.fn.dummy),
        'on_error': (None, season.util.fn.dummy)
    }

class ideConfig(base):
    DEFAULT_VALUES = {
        'acl': (None, season.util.fn.dummy)
    }

class buildConfig(base):
    DEFAULT_VALUES = {
        'command_ng': (str, 'ng'),
        'folder': (str, 'build'),
        'init': (None, None),
        'build': (None, None)
    }

class Config(season.util.std.stdClass):
    def __init__(self, server=None, **env):
        self.__server__ = server
        self.__env__ = env
        self.__cache__ = dict()

    def set(self, **env):
        for key in env:
            self.__env__[key] = env[key]

    def clean(self):
        remove_keys = []
        for key in self.__cache__:
            if key in ['boot']:
                continue
            remove_keys.append(key)
        for key in remove_keys:
            del self.__cache__[key]
        self.__env__ = dict()

    def __getattr__(self, name):
        if name in self.__cache__:
            return self.__cache__[name]

        configclass = base
        if name == 'boot': configclass = bootConfig
        elif name == 'service': configclass = serviceConfig
        elif name == 'ide': configclass = ideConfig
        elif name == 'build': configclass = buildConfig

        def build_config(base_config=dict()):
            config = configclass(base_config)
            self.__cache__[name] = config
            return config

        server = self.__server__

        if server is None or server.path.config is None:
            return build_config()

        config_path = os.path.join(server.path.config, name + '.py')
        if os.path.isfile(config_path) == False:
            return build_config()
        
        with open(config_path, mode="rb") as file:
            _code = file.read().decode('utf-8')
            
            env = dict()
            env['__name__'] = config_path
            env['__file__'] = config_path

            wiz = server.wiz()
            logger = None
            if wiz is not None:
                logger = wiz.logger(f"[server/config/{name}]")
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
        