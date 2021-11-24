import time
import season
import traceback

class SocketRegister(season.stdClass):
    
    # just regist
    def __init__(self, framework, wiz, app_id, branch="master"):
        try:
            wiz.framework = framework
            self.__wiz__ = wiz
            self.__appid__ = app_id
            self.__branch__ = branch
    
            ctrl, wiz_instance = wiz.socket(app_id)
            if 'Controller' not in ctrl:
                self.register = []
                return 
            ctrl = ctrl['Controller']
        
            self.register = []
            self.__ctrl__ = ctrl
            self.__wis__ = wiz_instance
            fnnames = dir(ctrl)
            for fnname in fnnames:
                if fnname[:2] == '__': 
                    continue
                if hasattr(getattr(ctrl, fnname), '__call__') == False:
                    continue
                self.register.append(fnname)

        except Exception as e:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            errorlog = f"\033[91m[" + timestamp + "}][wiz][error][socket]\033[0m\n" + traceback.format_exc()
            print(errorlog)
            wiz.framework.socketio.emit("log", errorlog, namespace="/wiz", to=branch, broadcast=True)
            self.register = []

    def __getattr__(self, fnname):
        branch = self.__branch__
        app_id = self.__appid__
        wiz = self.__wiz__
        
        if fnname == '__startup__':
            return None

        def fn(framework, namespace, data):
            if branch != "master":
                cache_namespace = "/".join(namespace.split("/")[:-1])
            else:
                cache_namespace = namespace
            cache_namespace = cache_namespace[9:]

            try:
                wiz = framework.model("wiz", module="wiz").use()
                ctrl, wiz_instance = wiz.socket(app_id)

                try:
                    wiz_instance.socket = framework.socket
                    wiz_instance.socket.namespace = namespace
                    
                    wiz_instance.cache.namespace = ""
                    wiz_instance.cache = wiz_instance.cache.use("socket").use(cache_namespace)
                    wiz_instance.cache.enable()

                    ctrl = ctrl['Controller']
                    try: ctrl = ctrl(wiz_instance)
                    except: ctrl = ctrl()

                    ctrlfn = getattr(ctrl, fnname)
                    ctrlfn(wiz_instance, data)

                except Exception as e:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                    errorlog = f"\033[91m[" + timestamp + "}][wiz][error][socket][" + namespace + "][" + fnname + "]\033[0m\n" + traceback.format_exc()
                    print(errorlog)
                    wiz.framework.socketio.emit("log", errorlog, namespace="/wiz", to=branch, broadcast=True)
            except:
                pass

        return fn

import time

class Controller:
    def __init__(self, framework):
        self.namespaces = {}
        wiz = framework.model("wiz", module="wiz")
                
        # build master branch        
        apps = wiz.data.rows()
        for app in apps:            
            app_id = app['package']['id']
            namespace = app['package']['namespace']
            app = wiz.data.get(app_id)
            if 'socketio' not in app: continue
            if len(app['socketio']) == 0: continue
            ctrl = SocketRegister(framework, wiz, app_id)
            self.namespaces[namespace] = ctrl

        # build working branch
        # wiz = framework.model("wiz", module="wiz").use()
        branches = wiz.workspace.branches()

        for branch in branches:
            if branch == "master": continue
            wiz.workspace.checkout(branch)
            apps = wiz.data.rows()

            for app in apps:
                app_id = app['package']['id']
                namespace = app['package']['namespace']
                app = wiz.data.get(app_id)
                if 'socketio' not in app: continue
                if len(app['socketio']) == 0: continue
                ctrl = SocketRegister(framework, wiz, app_id, branch)
                self.namespaces[namespace + "/" + branch] = ctrl
