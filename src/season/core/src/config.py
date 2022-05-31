import os
import time
import season

class Config(season.util.std.stdClass):
    def __init__(self, name='config'):
        self.name = name

    @classmethod
    def load(self, branch, namespace='config'):
        c = Config(namespace)
        config_path = os.path.join(season.path.project, 'branch', branch, 'config', namespace + '.py')
        if os.path.isfile(config_path) == False:
            c.data = dict()
        try:
            with open(config_path, mode="rb") as file:
                _tmp = {'config': None}
                _code = file.read().decode('utf-8')
                exec(_code, _tmp)
                c.data = _tmp['config']
        except Exception as e:
            pass
        return c

    def get(self, key=None, _default=None):
        if key is None:
            return self.data
        if key in self.data:
            return self.data[key]
        return _default