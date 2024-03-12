import season
import traceback

class Config(season.util.stdClass):
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
        cachens = name + "#" + self.wiz.project()

        if cachens in self.__cache__:
            return self.__cache__[cachens]

        class ConfigBase(season.util.stdClass):
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
            self.__cache__[cachens] = config
            return config

        wiz = self.wiz

        fs = wiz.project.fs("config")
        config_path = name + '.py'
        if fs.isfile(config_path) == False:
            return build_config()

        cachens = f'config.code#{self.wiz.project()}'
        cache = wiz.server.cache.get(cachens, dict())
    
        namespace = config_path
        if namespace in cache:
            _code = cache[namespace]
        else:
            _code = fs.read(config_path, "")
            _code = compile(_code, config_path, 'exec')
            cache[namespace] = _code

        env = dict()
        env['__name__'] = config_path
        env['__file__'] = config_path

        logger = wiz.logger("config/{name}")
        env['print'] = logger
        env['display'] = logger
        env['server'] = wiz.server

        try:
            exec(_code, env)
        except Exception as e:
            if logger is not None:
                errormsg = f"error: config/{name}.py\n" + traceback.format_exc()
                logger(errormsg, level=logger.LOG_CRITICAL)
        
        config = season.util.stdClass()
        for key in env:
            if key.startswith("__") and key.endswith("__"): continue
            config[key] = env[key]

        return build_config(config)