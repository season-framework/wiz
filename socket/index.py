import sys

class Controller:
    def __init__(self, framework):
        _stdout = sys.stdout
        class stdout():
            def __init__(self, socketio):
                self.socketio = socketio
                
            def write(self, string):
                _stdout.write(string)
                self.socketio.emit("log", string, namespace="/wiz", broadcast=True)

            def flush(self):
                _stdout.flush()

        sys.stdout = stdout(framework.socketio)

    def __startup__(self, framework):
        pass

    def response(self, framework, data):
        pass