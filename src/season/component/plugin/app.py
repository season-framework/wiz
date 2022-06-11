import os
import season

from season.component.base.app import App as Base

class App(Base):
    def __init__(self, wiz):
        super().__init__(wiz)

    def basepath(self):
        return os.path.join(season.path.project, 'plugin', 'modules', self.wiz.id, "apps")

    def cachepath(self):
        return os.path.join(season.path.project, 'cache', 'plugin', 'modules', self.wiz.id, "apps")
