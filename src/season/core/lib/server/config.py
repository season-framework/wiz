import os
import season
import traceback

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
DEFAULT_FILE_MAP[".sass"] = 'code/scss'
DEFAULT_FILE_MAP[".scss"] = 'code/scss'
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
        elif attr == 'secret_key': return obj if obj is not None else "season-wiz"
        elif attr == 'wiz_url': return str(obj) if obj is not None else '/wiz'
        elif attr == 'http_port': return int(obj) if obj is not None else 3000
        elif attr == 'http_method': return obj if obj is not None else ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']
        elif attr == 'dev': return bool(obj) if obj is not None else False
        elif attr == 'jinja_variable_start_string': return str(obj) if obj is not None else '{$'
        elif attr == 'jinja_variable_end_string': return str(obj) if obj is not None else '$}'
        elif attr == 'build': return obj if obj is not None else None
        
        return obj

class wizconfig(base):
    def __getattr__(self, attr):
        obj = super(wizconfig, self).__getattr__(attr)
        if attr == 'theme': return obj if obj is not None else "default"
        elif attr == 'log_level': return int(obj) if obj is not None else 2
        elif attr == 'home': return obj if obj is not None else "ui/workspace"
        elif attr == 'plugin': return obj if obj is not None else ['workspace', 'branch']
        elif attr == 'category': return obj if obj is not None else [
            {'id': 'page', 'title': 'Page'},
            {'id': 'view', 'title': 'View'},
            {'id': 'modal', 'title': 'Modal'}
            ]
        elif attr == 'file_support':
            data = dict()
            for key in DEFAULT_FILE_MAP:
                data[key] = DEFAULT_FILE_MAP[key]
            if obj is not None:
                for key in obj:
                    data[key] = obj[key]
            obj = data
        elif attr == 'build_resource': return obj if obj is not None else None
        elif attr == 'before_request': return obj if obj is not None else None
        elif attr == 'after_request': return obj if obj is not None else None
        elif attr == 'on_error': return obj if obj is not None else None
        elif attr == 'acl': return obj if obj is not None else None

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

    def clean(self):
        self.cache = dict()

    def reload(self):
        try:
            server = self.cache['server']
        except:
            pass
        try:
            socketio = self.cache['socketio']
        except:
            pass
        try:
            install = self.cache['install']
        except:
            pass
        self.cache = dict()
        try:
            self.cache['server'] = server
        except:
            pass
        try:
            self.cache['socketio'] = socketio
        except:
            pass
        try:
            self.cache['install'] = install
        except:
            pass

    def __getattr__(self, name):        
        if name in self.cache:
            return self.cache[name]

        configclass = base
        if name == 'server': configclass = app
        elif name == 'wiz': configclass = wizconfig
        elif name == 'socketio': configclass = socketio

        config_path = os.path.join(season.path.project, 'config', name + '.py')
        if os.path.isfile(config_path) == False:
            config = configclass()
            self.cache[name] = config
            return config
        
        with open(config_path, mode="rb") as file:
            _code = file.read().decode('utf-8')
            
            env = dict()
            env['__name__'] = config_path
            env['__file__'] = config_path
            
            if 'wiz' in self.kwargs:
                wiz = self.kwargs['wiz']
                env['print'] = wiz.logger(f"[server/config/{name}]")
                env['display'] = env['print']
            
            try:
                exec(compile(_code, config_path, 'exec'), env)
            except Exception as e:
                if 'wiz' in self.kwargs:
                    wiz = self.kwargs['wiz']
                    errormsg = f"error: config/{name}.py\n" + traceback.format_exc()        
                    wiz.log(errormsg, level=season.log.error, color=91)

            config = season.stdClass()
            for key in env:
                if key.startswith("__") and key.endswith("__"): continue
                config[key] = env[key]
            config = configclass(config)
            
            self.cache[name] = config
            return config
        