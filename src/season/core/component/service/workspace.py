from season.core.component.base.workspace import Workspace as Base

class Workspace(Base):
    def __init__(self, wiz):
        super().__init__(wiz)

    def path(self, *args):
        return self.wiz.branch.path(*args)
        