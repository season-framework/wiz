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
        wiz = server.wiz()

        @socketio.on_error_default
        def sio_handle_exception_error(e):
            logger = server.wiz().logger("[SOCKET]")
            errormsg = traceback.format_exc()
            logger(errormsg, level=season.LOG_ERROR)

        # ide socket
        def wrapper(namespace, server, controller, fnname):
            def proceed(*args, **kwargs):
                data = None
                if len(args) == 1:
                    data = args[0]
                elif len(args) > 1:
                    data = args
                wiz = server.wiz()
                fn = getattr(ctrl, fnname)
                handler = SocketHandler(server, namespace)
                season.util.fn.call(fn, server=server, wiz=wiz, socketio=server.app.socketio, flask_socketio=server.package.flask_socketio, flask=server.package.flask, io=handler, data=data)

            return proceed

        namespace = wiz.uri.ide()
        ctrl = IdeController(server)
        for fnname in dir(ctrl):
            if fnname.startswith("__") and fnname.endswith("__"): continue
            proceed = season.util.fn.call(wrapper, namespace=namespace, server=server, controller=ctrl, fnname=fnname)
            socketio.on_event(fnname, proceed, namespace=namespace)