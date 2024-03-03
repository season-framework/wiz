import flask
import flask_socketio

class Package:
    def __init__(self):
        self.flask = flask
        self.socketio = self.flask_socketio = flask_socketio
