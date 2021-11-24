import season

class Model(season.interfaces.wiz.model.fs.Model):
    def __init__(self, framework):
        super().__init__(framework)
        self.set_path(season.core.PATH.WEBSRC)
        self.namespace = ''

    def use(self, namespace):
        model = Model(self.framework)
        model.namespace = namespace
        return model