class Controller:
    def __init__(self, framework):
        # TODO: socketio controller always to refresh
        self.namespaces = {}
        
        wiz = framework.model("wiz", module="wiz")
        apps = wiz.data.rows()
        
        for app in apps:
            app_id = app['package']['id']
            app = wiz.data.get(app_id)
            if 'socketio' not in app: continue
            if len(app['socketio']) == 0: continue

            namespace = app['package']['namespace']
            
            try:
                ctrl, wiz_instance = wiz.socket(app_id)
                ctrl = ctrl['Controller']
                ctrl = ctrl(wiz_instance)
                self.namespaces[namespace] = ctrl
            except:
                pass
