import season
import sys

NAMESPACE = "/wiz"

class Controller:
    def __init__(self, framework):
        _stdout = sys.stdout
        class stdout():
            def __init__(self, socketio):
                self.socketio = socketio
                
            def write(self, string):
                _stdout.write(string)
                self.socketio.emit("log", string, namespace=NAMESPACE, broadcast=True)

            def flush(self):
                _stdout.flush()

        sys.stdout = stdout(framework.socketio)

        self.session = season.stdClass()
        self.room_connection = dict()

    def __startup__(self, framework, _):
        config = framework.config.load("wiz")
        try:
            config.acl(framework)
        except:
            return

    def __status__(self, framework, room):
        msg = dict()
        msg['sid'] = framework.flask.request.sid
        msg['type'] = 'status'
        msg['room'] = room
        if room not in self.room_connection:
            return msg
        
        inroom = self.room_connection[room]
        users = dict()
        for user in inroom:
            userid = inroom[user]
            if userid not in users:
                users[userid] = 0
            users[userid] = users[userid] + 1
        msg['users'] = users

        return msg

    def connect(self, framework, _):
        config = framework.config.load("wiz")
        sid = framework.flask.request.sid
        self.session[sid] = season.stdClass()
        self.session[sid].sid = sid
        self.session[sid].uid = config.uid(framework)
        msg = dict()
        msg["type"] = "connect"
        msg["sid"] = sid
        framework.socket.emit("connect", msg, to=sid)

    def join(self, framework, data):
        if framework.flask.request.sid not in self.session:
            return
        
        sid = framework.flask.request.sid
        room = data["id"]
        self.session[sid]['room'] = room
        user_id = self.session[sid].uid

        if room not in self.room_connection: 
            self.room_connection[room] = dict()

        framework.flask_socketio.join_room(room, namespace=NAMESPACE)
        self.room_connection[room][sid] = user_id
        
        msg = self.__status__(framework, room)
        msg['join'] = room
        framework.socket.emit("message", msg, to=room, broadcast=True)

    def edit(self, framework, data):
        sid = framework.flask.request.sid
        if sid not in self.session:
            return
        room = self.session[sid]['room']
        data['sid'] = sid
        data['type'] = "edit"
        framework.socket.emit("message", data, to=room, broadcast=True)

    def leave(self, framework, data):
        if framework.flask.request.sid not in self.session:
            return
        
        sid = framework.flask.request.sid
        room = data["id"]

        framework.flask_socketio.leave_room(room, namespace=NAMESPACE)

        if room in self.room_connection:
            if sid in self.room_connection[room]:
                del self.room_connection[room][sid]

        msg = self.__status__(framework, room)
        framework.socket.emit("message", msg, to=room, broadcast=True)

    def disconnect(self, framework, _):
        if framework.flask.request.sid not in self.session:
            return
        
        sid = framework.flask.request.sid
        room = self.session[sid].room

        if room in self.room_connection:
            if sid in self.room_connection[room]:
                del self.room_connection[room][sid]

        if sid in self.session:
            del self.session[sid]

        msg = self.__status__(framework, room)
        framework.socket.emit("message", msg, to=room, broadcast=True)