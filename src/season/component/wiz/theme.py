import os
import season
from season.component.base.theme import Theme as Base

class Theme(Base):
    def __init__(self, wiz):
        super().__init__(wiz)

    def basepath(self):
        branch = self.branch()
        return os.path.join(season.path.project, "branch", branch, "themes")
