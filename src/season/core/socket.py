import os
import season
from werkzeug.exceptions import HTTPException
import traceback

class SocketHandler:
    def __init__(self, server, namespace):
        self.server = server
        self.namespace = namespace
    
    def emit(self, *args, **kwargs):
        socketio = self.server.app.socketio
        kwargs['namespace'] = self.namespace
        socketio.emit(*args, **kwargs)

    def send(self, message, **kwargs):
        socketio = self.server.app.socketio
        kwargs['namespace'] = self.namespace
        socketio.send(message, **kwargs)
    
    def join_room(self, room, sid=None):
        self.join(room, sid=sid)

    def join(self, room, sid=None):
        socketio = self.server.package.flask_socketio
        socketio.join_room(room, sid=sid, namespace=self.namespace)

    def leave_room(self, room, sid=None):
        self.leave(room, sid=sid)

    def leave(self, room, sid=None):
        socketio = self.server.package.flask_socketio
        socketio.leave_room(room, sid=sid, namespace=self.namespace)

    def status(self, channel='message', to=None, **msg):
        if 'type' not in msg: msg['type'] = 'status'
        acts = dict()
        acts['broadcast'] = True
        if to is not None: acts['to'] = to
        self.emit(channel, msg, **acts)

    def clients(self, room):
        sio = self.server.app.socketio.server
        clients = sio.manager.get_participants(self.namespace, room)
        clients = list(clients)
        return clients

    def rooms(self):
        sio = self.server.app.socketio.server
        rooms = []
        for room_name, room in sio.manager.rooms[self.namespace].items():
            rooms.append(room_name)
        return rooms

class IdeController:
    def __init__(self, server):
        self.server = server

    def connect(self):
        pass

    def join(self, flask, data, io):
        sid = flask.request.sid
        if 'id' not in data: return
        room = data['id']
        io.join(room)

    def leave(self, flask, data, io):
        sid = flask.request.sid
        if 'id' not in data: return
        room = data['id']
        io.leave(room)

    def disconnect(self, flask, io):
        sid = flask.request.sid

class Socket:
    def __init__(self, server):
        self.server = server

    def bind(self):
        server = self.server
        socketio = server.app.socketio
        app = server.app.flask
        wiz = server.wiz()

        @socketio.on_error_default
        def sio_handle_exception_error(e):
            logger = server.wiz().logger("[SOCKET]")
            errormsg = traceback.format_exc()
            logger(errormsg, level=season.LOG_ERROR)

        # app socket
        def wrapper_app(namespace, gwiz, fs, path, fnname):
            def proceed(*args, **kwargs):
                server = gwiz.server
                wiz = gwiz()

                code = fs.read(path)
                siopath = fs.abspath(path)
                logger = wiz.logger(f"[SOCKET][{namespace}/{fnname}]")

                ctrl = season.util.os.compiler(code, name=siopath, logger=logger, wiz=wiz)
                ctrl = ctrl['Controller']
                ctrl = season.util.fn.call(ctrl, server=server, wiz=wiz, socketio=server.app.socketio, flask_socketio=server.package.flask_socketio, flask=server.package.flask)
                fnlist = dir(ctrl)
                data = None
                if len(args) == 1:
                    data = args[0]
                elif len(args) > 1:
                    data = args

                fn = getattr(ctrl, fnname)
                handler = SocketHandler(server, namespace)
                season.util.fn.call(fn, server=server, wiz=wiz, socketio=server.app.socketio, flask_socketio=server.package.flask_socketio, flask=server.package.flask, io=handler, data=data)

            return proceed

        # ide socket
        if server.is_bundle == False:
            def wrapper(namespace, server, controller, fnname):
                def proceed(*args, **kwargs):
                    data = None
                    if len(args) == 1:
                        data = args[0]
                    elif len(args) > 1:
                        data = args
                    wiz = server.wiz()
                    fn = getattr(controller, fnname)
                    handler = SocketHandler(server, namespace)
                    season.util.fn.call(fn, server=server, wiz=wiz, socketio=server.app.socketio, flask_socketio=server.package.flask_socketio, flask=server.package.flask, io=handler, data=data)

                return proceed

            # default
            namespace = wiz.uri.ide()
            ctrl = IdeController(server)
            for fnname in dir(ctrl):
                if fnname.startswith("__") and fnname.endswith("__"): continue
                proceed = season.util.fn.call(wrapper, namespace=namespace, server=server, controller=ctrl, fnname=fnname)
                socketio.on_event(fnname, proceed, namespace=namespace)

            # ide apps
            workspace = wiz.workspace('ide')
            fs = workspace.fs("app")
            apps = fs.ls()
            logger = wiz.logger("[SOCKET]")
            for app_id in apps:
                try:
                    socketiofile = os.path.join(app_id, 'socket.py')
                    if fs.exists(socketiofile) == False:
                        continue

                    code = fs.read(socketiofile)
                    siopath = fs.abspath(socketiofile)
                    if len(code) == 0: continue

                    ctrl = season.util.os.compiler(code, name=siopath, logger=logger, wiz=wiz)
                    ctrl = ctrl['Controller']
                    ctrl = season.util.fn.call(ctrl, server=server, wiz=wiz, socketio=server.app.socketio, flask_socketio=server.package.flask_socketio, flask=server.package.flask)
                    fnlist = dir(ctrl)
                    for fnname in fnlist:
                        if fnname.startswith("__") and fnname.endswith("__"): continue
                        namespace = wiz.uri.ide() + f"/app/{app_id}"
                        proceed = wrapper_app(namespace, wiz, fs, socketiofile, fnname)
                        socketio.on_event(fnname, proceed, namespace=namespace)

                    logger(f"socketio binded: `{namespace}`", level=season.LOG_INFO)
                except Exception as e:
                    logger(f"`{app_id}` socketio file not binded at /wiz/ide:\n" + str(e), level=season.LOG_ERROR)

        # branch sockets
        branches = wiz.branch.list()
        if server.is_bundle:
            branches = ["main"]

        for branch in branches:
            wiz = server.wiz()()
            wiz.branch(branch)
            workspace = wiz.workspace("service")
            fs = workspace.fs("src", "app")

            logger = wiz.logger("[SOCKET]")
            apps = fs.list()
            for app_id in apps:
                try:
                    socketiofile = os.path.join(app_id, 'socket.py')
                    if fs.exists(socketiofile) == False:
                        continue

                    code = fs.read(socketiofile)
                    siopath = fs.abspath(socketiofile)
                    if len(code) == 0: continue

                    ctrl = season.util.os.compiler(code, name=siopath, logger=logger, wiz=wiz)
                    ctrl = ctrl['Controller']
                    ctrl = season.util.fn.call(ctrl, server=server, wiz=wiz, socketio=server.app.socketio, flask_socketio=server.package.flask_socketio, flask=server.package.flask)
                    fnlist = dir(ctrl)
                    for fnname in fnlist:
                        if fnname.startswith("__") and fnname.endswith("__"): continue
                        namespace = wiz.uri.wiz() + f"/app/{branch}/{app_id}"
                        proceed = wrapper_app(namespace, wiz, fs, socketiofile, fnname)
                        socketio.on_event(fnname, proceed, namespace=namespace)

                    logger(f"socketio binded: `{namespace}`", level=season.LOG_INFO)
                except Exception as e:
                    logger(f"`{app_id}` socketio file not binded at `{branch}` branch:\n" + str(e), level=season.LOG_ERROR)
