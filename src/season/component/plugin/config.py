import os
import season

class base(season.util.std.stdClass):
    pass

class _config(base):
    def __getattr__(self, attr):
        obj = super(_config, self).__getattr__(attr)
        
        # default values
        if attr == 'theme': return obj if obj is not None else "default"

        return obj

class Config(season.util.std.stdClass):

    @classmethod
    def load(self, name='config'):
        configclass = base
        if name == 'config': configclass = _config
        
        config_path = os.path.join(season.path.project, 'plugin', 'config', name + '.py')
        if os.path.isfile(config_path) == False:
            return configclass()
        
        try:
            with open(config_path, mode="rb") as file:
                _tmp = {'config': None}
                _code = file.read().decode('utf-8')
                exec(_code, _tmp)
                config = _tmp['config']
                return configclass(config)
        except Exception as e:
            pass

        return configclass()
