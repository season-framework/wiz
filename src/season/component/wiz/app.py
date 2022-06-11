import os
import season

from season.component.base.app import App as Base

class App(Base):
    def __init__(self, wiz):
        super().__init__(wiz)

    def basepath(self):
        branch = self.branch()
        return os.path.join(season.path.project, "branch", branch, "apps")

    def cachepath(self):
        branch = self.branch()
        return os.path.join(season.path.project, "cache", "branch", branch, "apps")
