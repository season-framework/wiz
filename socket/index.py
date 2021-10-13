import sys

class ControllerSub:
    def __startup__(self, framework):
        framework.socket.emit("startup /wiz/testme socket")
        framework.session = framework.lib.session.to_dict()

    def response(self, framework, data):
        framework.socket.emit("hello world")

class Controller:
    def __init__(self, framework):
        # syslog capture
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

        # set namespaces
        self.namespaces = {}
        self.namespaces["testme"] = ControllerSub()

    def __startup__(self, framework):
        framework.socket.emit("startup /wiz socket")
        framework.session = framework.lib.session.to_dict()

    def response(self, framework, data):
        framework.socket.emit("hello world")