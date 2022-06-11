import os
import season
import time
import traceback
from werkzeug.exceptions import HTTPException

from season.core.lib.server.handler.socketio import plugin

class SocketHandler:
    def __init__(self, wiz, namespace):
        self.wiz = wiz
        self.namespace = namespace
    
    def emit(self, *args, **kwargs):
        socketio = self.wiz.server.wsgi.socketio
        kwargs['namespace'] = self.namespace
        socketio.emit(*args, **kwargs)

    def send(self, message, **kwargs):
        socketio = self.wiz.server.wsgi.socketio
        kwargs['namespace'] = self.namespace
        socketio.send(message, **kwargs)
    
    def join_room(self, room, sid=None):
        self.join(room, sid=sid)

    def join(self, room, sid=None):
        socketio = self.wiz.server.flask_socketio
        socketio.join_room(room, sid=sid, namespace=self.namespace)

    def leave_room(self, room, sid=None):
        self.leave(room, sid=sid)

    def leave(self, room, sid=None):
        socketio = self.wiz.server.flask_socketio
        socketio.leave_room(room, sid=sid, namespace=self.namespace)

    def status(self, channel='message', to=None, **msg):
        if 'type' not in msg: msg['type'] = 'status'
        acts = dict()
        acts['broadcast'] = True
        if to is not None: acts['to'] = to
        self.emit(channel, msg, **acts)

    def clients(self, room):
        sio = self.wiz.server.wsgi.socketio.server
        clients = sio.manager.get_participants(self.namespace, room)
        clients = list(clients)
        return clients

    def rooms(self):
        sio = self.wiz.server.wsgi.socketio.server
        rooms = []
        for room_name, room in sio.manager.rooms[self.namespace].items():
            rooms.append(room_name)
        return rooms

# for plugins
def wrapper(namespace, wiz, ctrl, fnname):
    def proceed(*args, **kwargs):
        data = None
        if len(args) == 1:
            data = args[0]
        elif len(args) > 1:
            data = args
        fn = getattr(ctrl, fnname)
        handler = SocketHandler(wiz, namespace)
        season.util.fn.call(fn, wiz=wiz, socketio=wiz.server.wsgi.socketio, flask_socketio=wiz.server.flask_socketio, flask=wiz.server.flask, io=handler, data=data)

    return proceed

# for apps
def wrapper_code(namespace, wiz, logger, fs, path, fnname):
    def proceed(*args, **kwargs):
        code = fs.read(path)
        siopath = fs.abspath(path)
        ctrl = season.util.os.compiler(code, name=siopath, logger=logger, wiz=wiz)
        ctrl = ctrl['Controller']()
        fnlist = dir(ctrl)
        data = None
        if len(args) == 1:
            data = args[0]
        elif len(args) > 1:
            data = args
        fn = getattr(ctrl, fnname)
        handler = SocketHandler(wiz, namespace)
        season.util.fn.call(fn, wiz=wiz, socketio=wiz.server.wsgi.socketio, flask_socketio=wiz.server.flask_socketio, flask=wiz.server.flask, io=handler, data=data)

    return proceed

class SocketIO:
    def __init__(self, server):
        wiz = server.wiz

        socketio = server.wsgi.socketio
        logger = wiz.logger(tag="[socketio]", log_color=91, trace=False)

        @socketio.on_error_default
        def sio_handle_exception_error(e):
            errormsg = traceback.format_exc()
            logger(errormsg, level=season.log.error, color=91)

        # namespace for wiz plugin
        wizurl = server.config.server.wiz_url
        if wizurl[-1] == "/": wizurl = wizurl[:-1]
        ctrl = plugin.Controller(server.wiz)
        fnlist = dir(ctrl)
        for fnname in fnlist:
            if fnname.startswith("__") and fnname.endswith("__"): continue
            socketio.on_event(fnname, wrapper(wizurl, wiz, ctrl, fnname), namespace=wizurl)

        # bind wiz.io() for apps
        def find_io(wiz):
            def fn(app_id):
                branch = wiz.branch()
                namespace = wizurl + f"/app/{branch}/{app_id}"
                return SocketHandler(wiz, namespace)
            return fn
        wiz.io = find_io(wiz)

        # bind plugin.io() for apps
        def find_plugin_io(wiz):
            plugin_id = wiz.id
            def fn(app_id):
                namespace = wizurl + f"/plugin/{plugin_id}/{app_id}"
                return SocketHandler(wiz, namespace)
            return fn

        def wiz_socket_bind():
            # namespace for wiz plugins
            pluginfs = season.util.os.FileSystem(os.path.join(season.path.project, 'plugin', 'modules'))
            plugins = pluginfs.list()
            for plugin_id in plugins:
                appfs = pluginfs.use(os.path.join(plugin_id, 'apps'))
                apps = appfs.list()
                plugin = season.plugin(server).load(plugin_id)
                plugin.io = find_plugin_io(plugin)
                for app_id in apps:
                    try:
                        logger_dev = plugin.logger(tag=f"[socketio][plugin][{plugin_id}][{app_id}]", trace=False)
                        socketiofile = os.path.join(app_id, 'socketio.py')
                        if appfs.exists(socketiofile) == False:
                            continue
                        code = appfs.read(socketiofile)
                        siopath = appfs.abspath(socketiofile)
                        if len(code) == 0: continue
                        ctrl = season.util.os.compiler(code, name=siopath, logger=logger_dev, wiz=plugin)
                        ctrl = ctrl['Controller']()
                        fnlist = dir(ctrl)

                        for fnname in fnlist:
                            if fnname.startswith("__") and fnname.endswith("__"): continue
                            namespace = wizurl + f"/plugin/{plugin_id}/{app_id}"
                            socketio.on_event(fnname, wrapper_code(namespace, plugin, logger_dev, appfs, os.path.join(app_id, 'socketio.py'), fnname), namespace=namespace)
                        logger(f"socketio binded: `{namespace}`", color=94, level=season.log.info)
                    except Exception as e:
                        logger(f"`{app_id}` plugin socketio file not binded at `{plugin_id}` plugin:\n" + str(e))

            # namespace for wiz apps
            branches = server.wiz.branches()
            for branch in branches:
                wiz = season.wiz(server)
                wiz.__branch__ = branch
                wiz.io = find_io(wiz)
                
                path = os.path.join(season.path.project, 'branch', branch, 'apps')
                fs = season.util.os.FileSystem(path)
                apps = fs.list()
                for app_id in apps:
                    logger_dev = wiz.logger(tag=f"[socketio][{branch}][{app_id}]", trace=False)
                    try:
                        socketiofile = os.path.join(app_id, 'socketio.py')
                        if fs.exists(socketiofile) == False:
                            continue
                        code = fs.read(os.path.join(app_id, 'socketio.py'))
                        siopath = fs.abspath(os.path.join(app_id, 'socketio.py'))
                        if len(code) == 0: continue

                        ctrl = season.util.os.compiler(code, name=siopath, logger=logger_dev, wiz=wiz)
                        ctrl = ctrl['Controller']()
                        fnlist = dir(ctrl)

                        for fnname in fnlist:
                            if fnname.startswith("__") and fnname.endswith("__"): continue
                            namespace = wizurl + f"/app/{branch}/{app_id}"
                            socketio.on_event(fnname, wrapper_code(namespace, wiz, logger_dev, fs, os.path.join(app_id, 'socketio.py'), fnname), namespace=namespace)

                        logger(f"socketio binded: `{namespace}`", color=94, level=season.log.info)
                    except Exception as e:
                        logger(f"`{app_id}` socketio file not binded at `{branch}` branch:\n" + str(e))

        self.bind = wiz_socket_bind
        wiz_socket_bind()