import os
import season
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
        socketio = server.app.socketio

        def createWiz():
            return season.lib.core.Wiz(server)

        @socketio.on_error_default
        def sio_handle_exception_error(e):
            wiz = createWiz()
            logger = wiz.logger("ide", "sock", "error")
            errormsg = traceback.format_exc()
            logger(errormsg, level=season.LOG_ERROR)

        def wrapper(fn, namespace):
            def proceed(*args, **kwargs):
                data = None
                if len(args) == 1: data = args[0]
                elif len(args) > 1: data = args

                params = dict()
                params['server'] = server
                params['wiz'] = createWiz()
                params['socketio'] = server.app.socketio
                params['flask_socketio'] = server.package.flask_socketio
                params['flask'] = server.package.flask
                params['io'] = SocketHandler(server, namespace)
                params['data'] = data

                season.util.compiler(fn).call(**params)

            return proceed
        
        # ide socket
        def sio_handle_ide():
            wiz = createWiz()

            # default
            namespace = wiz.uri.ide("ide")
            ctrl = IdeController(server)
            for fnname in dir(ctrl):
                if fnname.startswith("__") and fnname.endswith("__"): continue
                proceed = wrapper(getattr(ctrl, fnname), namespace)
                socketio.on_event(fnname, proceed, namespace=namespace)

            # ide apps
            fs = wiz.ide.fs("app")
            apps = fs.ls()
            logger = wiz.logger("ide", "sock", "app")
            for app_id in apps:
                try:
                    socketiofile = os.path.join(app_id, 'socket.py')
                    if fs.exists(socketiofile) == False:
                        continue

                    code = fs.read(socketiofile)
                    siopath = fs.abspath(socketiofile)
                    if len(code) == 0: continue

                    ctrl = season.util.compiler().build(code, name=siopath, logger=logger, wiz=wiz).fn
                    ctrl = ctrl['Controller']
                    ctrl = season.util.compiler(ctrl).call(server=server, wiz=wiz, socketio=server.app.socketio, flask_socketio=server.package.flask_socketio, flask=server.package.flask)
                    fnlist = dir(ctrl)
                    for fnname in fnlist:
                        if fnname.startswith("__") and fnname.endswith("__"): continue
                        namespace = wiz.uri.ide("ide") + f"/app/{app_id}"
                        proceed = wrapper(getattr(ctrl, fnname), namespace)
                        socketio.on_event(fnname, proceed, namespace=namespace)

                    logger(f"socketio binded: `{namespace}`", level=season.LOG_INFO)
                except Exception as e:
                    logger(f"`{app_id}` socketio file not binded at ide:\n" + str(e), level=season.LOG_ERROR)

        # projects socket
        def sio_handle_project():
            wiz = createWiz()
            projects = wiz.project.list()
            if server.config.boot.bundle:
                projects = ["main"]

            for project in projects:
                wiz = createWiz()
                wiz.project(project)
                fs = wiz.project.fs("bundle", "src", "app")
                
                logger = wiz.logger("sock")
                apps = fs.list()

                for app_id in apps:
                    try:
                        socketiofile = os.path.join(app_id, 'socket.py')
                        if fs.exists(socketiofile) == False:
                            continue

                        code = fs.read(socketiofile)
                        siopath = fs.abspath(socketiofile)
                        if len(code) == 0: continue

                        ctrl = season.util.compiler().build(code, name=siopath, logger=logger, wiz=wiz).fn
                        ctrl = ctrl['Controller']
                        ctrl = season.util.compiler(ctrl).call(server=server, wiz=wiz, socketio=server.app.socketio, flask_socketio=server.package.flask_socketio, flask=server.package.flask)
                        fnlist = dir(ctrl)
                        for fnname in fnlist:
                            if fnname.startswith("__") and fnname.endswith("__"): continue
                            namespace = wiz.uri.ide() + f"/app/{project}/{app_id}"
                            proceed = wrapper(getattr(ctrl, fnname), namespace)
                            socketio.on_event(fnname, proceed, namespace=namespace)

                        logger(f"socketio binded: `{namespace}`", level=season.LOG_INFO)
                    except Exception as e:
                        logger(f"`{app_id}` socketio file not binded at `{project}` project:\n" + str(e), level=season.LOG_ERROR)

        if server.config.boot.bundle == False:
            sio_handle_ide()
        sio_handle_project()
