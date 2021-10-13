class Controller:
    def __init__(self, framework):
        # set namespaces
        self.namespaces = {}
        wiz = framework.model("wiz", module="wiz")
        wizsocs = wiz.rows(fields="namespace,socketio", where="`socketio` is not Null")
        for wizsoc in wizsocs:
            namespace = wizsoc['namespace']
            ctrlcode = wizsoc['socketio']

            fn = {'__file__': 'season.Spawner', '__name__': 'season.Spawner', 'framework': framework}
            exec(compile(ctrlcode, 'season.Spawner', 'exec'), fn)
            ctrl = None
            try:
                ctrl = fn['Controller'](framework)
            except:
                try:
                    ctrl = fn['Controller']
                except:
                    ctrl = None
            self.namespaces[namespace] = ctrl

    def response(self, framework, data):
        pass