import os
import season
from season.component.base.route import Route as Base

class Route(Base):
    def __init__(self, wiz):
        super().__init__(wiz)

    def basepath(self):
        branch = self.branch()
        return os.path.join(season.path.project, "branch", branch, "routes")

    def cachepath(self):
        branch = self.branch()
        return os.path.join(season.path.project, "cache", "branch", branch, "routes")
