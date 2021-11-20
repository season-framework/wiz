import season

class Empty:
    def __init__(self, framework):
        self.framework = framework

class MySQL(season.core.interfaces.model.MySQL):
    def __init__(self, framework):
        super().__init__(framework)

    def getMessage(self):
        return self.framework.lib.util.randomstring()
