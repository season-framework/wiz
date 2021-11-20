class Model(wiz.model("mysql/base")):
    def __init__(self):
        super().__init__()
        self.namespace = "mysql"
        self.tablename = "test"