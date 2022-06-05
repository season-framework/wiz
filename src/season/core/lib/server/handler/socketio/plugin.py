class Controller:
    def __init__(self, wiz):
        pass

    def connect(self):
        pass

    def join(self, wiz, data, handler):
        sid = wiz.flask.request.sid
        room = data['id']
        handler.join(room)

    def leave(self, wiz, data, handler):
        sid = wiz.flask.request.sid
        room = data['id']
        handler.leave(room)

    def disconnect(self, wiz, handler):
        sid = wiz.flask.request.sid