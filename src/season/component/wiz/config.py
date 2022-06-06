import os
import season

class Config(season.util.std.stdClass):
    def __init__(self, name='config'):
        self.name = name
        self.data = {}

    @classmethod
    def load(self, wiz, branch, namespace='config'):
        c = Config(namespace)
        config_path = os.path.join(season.path.project, 'branch', branch, 'config', namespace + '.py')
        if os.path.isfile(config_path) == False:
            c.data = dict()
        try:
            with open(config_path, mode="rb") as file:
                code = file.read().decode('utf-8')
                env = {}
                env['wiz'] = wiz
                env['print'] = wiz.logger(f"[config/{namespace}]")
                env['display'] = env['print']
                
                predefined = []
                for key in env: predefined.append(key)

                exec(compile(code, config_path, 'exec'), env)

                config = season.stdClass()
                for key in env:
                    if key in predefined: continue
                    if key.startswith("__") and key.endswith("__"): continue
                    config[key] = env[key]

                c.data = config
        except Exception as e:
            errormsg = f"error: config/{name}.py\n" + traceback.format_exc()
            wiz.log(errormsg, level=season.log.error, color=91)
        return c

    def get(self, key=None, _default=None):
        if key is None:
            return self.data
        if key in self.data:
            return self.data[key]
        return _default