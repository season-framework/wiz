import sys

class Controller:
    def __init__(self, framework):
        _stdout = sys.stdout
        class stdout():
            def __init__(self, socketio):
                self.socketio = socketio
                
            def write(self, string):
                self.socketio.emit("log", string, namespace="/wiz", broadcast=True)
                _stdout.write(string)

            def flush(self):
                _stdout.flush()

        sys.stdout = stdout(framework.socketio)

    def __startup__(self, framework):
        framework.socket.emit("startup /wiz socket")

    def response(self, framework, data):
        framework.socket.emit("hello world")