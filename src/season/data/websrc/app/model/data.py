import season

class Model(season.interfaces.model.MySQL):
    def __init__(self, framework):
        super().__init__(framework)
        self.namespace = 'mysql' # database config namespace
        self.tablename = 'tablename' # tablename