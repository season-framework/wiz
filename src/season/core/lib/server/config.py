import os
import season

class base(season.util.std.stdClass):
    pass

class app(base):
    def __getattr__(self, attr):
        obj = super(app, self).__getattr__(attr)
        
        # default values
        if attr == 'http_host': return obj if obj is not None else "0.0.0.0"
        elif attr == 'http_port': return int(obj) if obj is not None else 3000
        elif attr == 'http_method': return obj if obj is not None else ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']
        elif attr == 'dev': return bool(obj) if obj is not None else False
        elif attr == 'log_level': return int(obj) if obj is not None else 2
        elif attr == 'jinja_variable_start_string': return str(obj) if obj is not None else '{$'
        elif attr == 'jinja_variable_end_string': return str(obj) if obj is not None else '$}'
        elif attr == 'on_error': return obj if obj is not None else None
        elif attr == 'before_request': return obj if obj is not None else None
        elif attr == 'after_request': return obj if obj is not None else None
        elif attr == 'build': return obj if obj is not None else None
        elif attr == 'build_resource': return obj if obj is not None else None

        return obj

class wiz(base):
    def __getattr__(self, attr):
        obj = super(wiz, self).__getattr__(attr)
        if attr == 'url': return str(obj) if obj is not None else '/wiz'
        return obj

class socketio(base):
    def __getattr__(self, attr):
        obj = super(socketio, self).__getattr__(attr)
        if attr == 'run': return obj if obj is not None else dict()
        return obj

class Config(season.util.std.stdClass):

    @classmethod
    def load(self, name='server'):
        configclass = base
        if name == 'server': configclass = app
        elif name == 'wiz': configclass = wiz
        elif name == 'socketio': configclass = socketio

        config_path = os.path.join(season.path.project, 'config', name + '.py')
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
