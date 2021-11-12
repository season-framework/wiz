import season
import json

class Controller(season.interfaces.wiz.ctrl.admin.base.api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def search(self, framework):
        rows = self.wiz.rows(route=True)
        framework.response.status(200, rows)

    def info(self, framework):
        app_id = framework.request.segment.get(0, True)
        info = self.wiz.get(app_id, route=True)
        if info is None:
            framework.response.status(404)
        framework.response.status(200, info)

    def update(self, framework):
        info = framework.request.query("info", True)
        info = json.loads(info)
        self.wiz.update(info, route=True)
        framework.response.status(200)

    def delete(self, framework):
        app_id = framework.request.segment.get(0, True)
        self.wiz.delete(app_id, route=True)
        framework.response.status(200)