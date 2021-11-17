import season
import pymysql
import json
from werkzeug.exceptions import HTTPException

class Controller(season.interfaces.wiz.ctrl.admin.branch.api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def create(self, framework):
        branch = framework.request.query("branch", True)
        base = framework.request.query("base", "master")
        framework.wiz.workspace.checkout(branch, base)
        framework.response.cookies.set("season-wiz-branch", branch)
        framework.response.status(200, True)
