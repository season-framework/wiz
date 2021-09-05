import season

class Model(season.core.interfaces.model.FileSystem):
    def __init__(self, framework):
        super().__init__(framework)
        wizconfig = framework.config.load('wiz')
        self.config = season.stdClass()
        self.config.path = wizconfig.wizsrc
        self.namespace = ''

    def set_namespace(self, namespace):
        self.namespace = namespace

    def set_path(self, path):
        self.config.path = path

    def read(self, source, default=""):
        try:
            return self.read_text(source)
        except:
            return default