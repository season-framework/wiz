class Controller:
    def __init__(self, framework):
        self.namespaces = {}
        dev = framework.config.load().get("dev", False)
        wiz = framework.model("wiz", module="wiz")
        if dev:
            version = "master"
        else:
            version = wiz.deploy_version()
        wizsocs = wiz.rows(version=version, fields="namespace,socketio", where="`socketio` is not Null")
        
        _prelogger = framework.log

        for wizsoc in wizsocs:
            namespace = wizsoc['namespace']
            ctrlcode = wizsoc['socketio']

            fn = {'__file__': 'season.Spawner', '__name__': 'season.Spawner', 'framework': framework}
            exec(compile(ctrlcode, 'season.Spawner', 'exec'), fn)
            ctrl = None
            try:
                def _logger(*args):
                    _prelogger(f"[{namespace}]", *args)
                framework.log = _logger
                ctrl = fn['Controller'](framework)
            except Exception as e:
                try:
                    ctrl = fn['Controller']
                except:
                    ctrl = None
            if ctrl is not None:
                self.namespaces[namespace] = ctrl