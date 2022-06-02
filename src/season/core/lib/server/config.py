import os
import season

DEFAULT_FILE_MAP = {}
DEFAULT_FILE_MAP[".png"] = "image"
DEFAULT_FILE_MAP[".jpeg"] = "image"
DEFAULT_FILE_MAP[".jpg"] = "image"
DEFAULT_FILE_MAP[".ico"] = "image"
DEFAULT_FILE_MAP[".icon"] = "image"
DEFAULT_FILE_MAP[".py"] = 'code/python'
DEFAULT_FILE_MAP[".js"] = 'code/javascript'
DEFAULT_FILE_MAP[".ts"] = 'code/typescript'
DEFAULT_FILE_MAP[".css"] = 'code/css'
DEFAULT_FILE_MAP[".less"] = 'code/less'
DEFAULT_FILE_MAP[".sass"] = 'code/sass'
DEFAULT_FILE_MAP[".html"] = 'code/html'
DEFAULT_FILE_MAP[".pug"] = 'code/pug'
DEFAULT_FILE_MAP[".json"] = 'code/json'
DEFAULT_FILE_MAP[".svg"] = 'code/html'
DEFAULT_FILE_MAP[".txt"] = 'code/text'
DEFAULT_FILE_MAP[".map"] = 'code/json'
DEFAULT_FILE_MAP[".crt"] = 'code/text'
DEFAULT_FILE_MAP[".key"] = 'code/text'
DEFAULT_FILE_MAP[".sql"] = 'code/text'

class base(season.util.std.stdClass):
    pass

class app(base):
    def __getattr__(self, attr):
        obj = super(app, self).__getattr__(attr)
        
        # default values
        if attr == 'http_host': return obj if obj is not None else "0.0.0.0"
        elif attr == 'wiz_url': return str(obj) if obj is not None else '/wiz'
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

class wizconfig(base):
    def __getattr__(self, attr):
        obj = super(wizconfig, self).__getattr__(attr)
        if attr == 'theme': return obj if obj is not None else "default"
        if attr == 'home': return obj if obj is not None else "ui/workspace"
        if attr == 'plugin': return obj if obj is not None else ['workspace', 'branch']
        if attr == 'category': return obj if obj is not None else [
            {'id': 'page', 'title': 'Page'},
            {'id': 'view', 'title': 'View'},
            {'id': 'modal', 'title': 'Modal'}
            ]
        if attr == 'file_support':
            data = dict()
            for key in DEFAULT_FILE_MAP:
                data[key] = DEFAULT_FILE_MAP[key]
            if obj is not None:
                for key in obj:
                    data[key] = obj[key]
            obj = data
        return obj

class socketio(base):
    def __getattr__(self, attr):
        obj = super(socketio, self).__getattr__(attr)
        if attr == 'run': return obj if obj is not None else dict()
        return obj

class Config(season.util.std.stdClass):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.cache = dict()

    def set(self, **kwargs):
        for key in kwargs:
            self.kwargs[key] = kwargs[key]

    def reload(self):
        server = self.cache['server']
        socketio = self.cache['socketio']
        self.cache = dict()
        self.cache['server'] = server
        self.cache['socketio'] = socketio

    def __getattr__(self, name):
        config_id = f'server.config.{name}'
        
        if 'wiz' in self.kwargs:
            wiz = self.kwargs['wiz']
            if wiz.memory is not None:
                if config_id in wiz.memory:
                    return wiz.memory[config_id]

        cache_allowed = ['server', 'socketio', 'wiz']
        if name in self.cache and name in cache_allowed:
            return self.cache[name]

        configclass = base
        if name == 'server': configclass = app
        elif name == 'wiz': configclass = wizconfig
        elif name == 'socketio': configclass = socketio

        config_path = os.path.join(season.path.project, 'config', name + '.py')
        if os.path.isfile(config_path) == False:
            config = configclass()
            if name in cache_allowed: self.cache[name] = config
            return config
        
        with open(config_path, mode="rb") as file:
            _tmp = self.kwargs
            if 'wiz' in _tmp:
                wiz = _tmp['wiz']
                _tmp['print'] = wiz.logger(f"[server/config/{name}]")
                _tmp['display'] = _tmp['print']

            _code = file.read().decode('utf-8')
            exec(_code, _tmp)
            config = _tmp['config']
            config = configclass(config)
            
            if name in cache_allowed: 
                self.cache[name] = config
            
            if 'wiz' in _tmp:
                wiz = _tmp['wiz']
                if wiz.memory is not None:
                    wiz.memory[config_id] = config        

            return config
        