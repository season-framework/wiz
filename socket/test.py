import season

class Controller:
    def __init__(self, framework):
        self.framework = framework
        self.register = ["response"]

    def __startup__(self, framework):
        pass

    def response(self, framework, data):
        framework.socket.emit("hello test")