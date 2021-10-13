import season

class Controller:
    def __init__(self, framework):
        self.framework = framework
        self.register = ["response"]

    def response(self, framework, data):
        framework.socket.emit("hello")