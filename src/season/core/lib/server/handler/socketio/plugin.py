class Controller:
    def __init__(self, wiz):
        pass

    def connect(self):
        pass

    def join(self, wiz, data, io):
        sid = wiz.flask.request.sid
        if 'id' not in data: return
        room = data['id']
        io.join(room)

    def leave(self, wiz, data, io):
        sid = wiz.flask.request.sid
        if 'id' not in data: return
        room = data['id']
        io.leave(room)

    def disconnect(self, wiz, io):
        sid = wiz.flask.request.sid