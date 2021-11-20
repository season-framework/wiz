import season
import sys

NAMESPACE = "/wiz"

class Controller:
    def __init__(self, framework):
        self.session = season.stdClass()
        self.room_connection = dict()

    def __startup__(self, framework, _):
        self.config = config = framework.config.load("wiz")
        config.acl(framework)
        
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
        config = self.config
        sid = framework.flask.request.sid
        self.session[sid] = season.stdClass()
        self.session[sid].sid = sid
        self.session[sid].uid = sid
        msg = dict()
        msg["type"] = "connect"
        msg["sid"] = sid
        framework.socket.emit("connect", msg, to=sid)

    def join(self, framework, data):
        if framework.flask.request.sid not in self.session: return
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