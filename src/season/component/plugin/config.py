import os
import season

class base(season.util.std.stdClass):
    pass

class _config(base):
    def __getattr__(self, attr):
        obj = super(_config, self).__getattr__(attr)
        if attr == 'menu': return obj if obj is not None else []
        return obj

class Config(season.util.std.stdClass):

    @classmethod
    def load(self, wiz, name='config'):
        configclass = base
        if name == 'config': configclass = _config

        plugin_id = wiz.id
        if wiz.id is None: plugin_id = "default"

        config_path = os.path.join(season.path.project, 'plugin', 'modules', plugin_id, 'config', name + '.py')

        if os.path.isfile(config_path) == False:
            return configclass()
        
        with open(config_path, mode="rb") as file:
            code = file.read().decode('utf-8')
            logger = wiz.logger(f"[plugin/config/{name}]")
            config = season.util.os.compiler(code, name=config_path, logger=logger, wiz=wiz)
            if 'config' in config: config = config['config']
            else: config = dict()
            return configclass(config)
        
        return configclass()
