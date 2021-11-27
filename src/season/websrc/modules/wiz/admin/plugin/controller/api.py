import os
import season
import json

class Controller(season.interfaces.wiz.ctrl.admin.plugin.api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def list(self, framework):
        rows = self.plugin.list()
        framework.response.status(200, rows)

    def info(self, framework):
        plugin_id = framework.request.segment.get(0, True)
        info = self.plugin.get(plugin_id)
        if info is None:
            framework.response.status(404)
        framework.response.status(200, info)

    def create(self, framework):
        plugin_id = framework.request.query("id", True)
        name = framework.request.query("name", True)

        status = self.plugin.create(plugin_id, name)
        framework.response.status(200)
        
    def update(self, framework):
        plugin_id = framework.request.segment.get(0, True)
        info = framework.request.query("info", True)
        apps = framework.request.query("apps", True)
        route = framework.request.query("route", True)

        status = self.plugin.update(plugin_id, info, apps, route)

        if status:
            framework.response.status(200)
        framework.response.status(500)

    def delete(self, framework):
        plugin_id = framework.request.segment.get(0, True)
        self.plugin.delete(plugin_id)
        framework.response.status(200)
