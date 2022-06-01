import os
import season
from season.component.base.route import Route as Base

class Route(Base):
    def __init__(self, wiz):
        super().__init__(wiz)

    def basepath(self):
        return os.path.join(season.path.project, 'plugin', 'modules', self.wiz.id, "routes")

    def cachepath(self):
        return os.path.join(season.path.project, 'cache', 'plugin', 'modules', self.wiz.id, "routes")
