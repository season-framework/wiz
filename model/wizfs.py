import season

class Model(season.core.interfaces.model.FileSystem):
    def __init__(self, framework):
        super().__init__(framework)
        self.config = season.stdClass()
        self.config.path = season.core.PATH.WEBSRC
        self.namespace = ''

    def use(self, namespace):
        self.namespace = namespace
        return self

    def list(self):
        return super().files()