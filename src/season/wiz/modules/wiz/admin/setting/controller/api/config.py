import season
import pymysql
import json
import datetime
from werkzeug.exceptions import HTTPException

class Controller(season.interfaces.wiz.ctrl.admin.setting.api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def packageinfo(self, framework):
        package = framework.model("config", module="wiz").get()        
        framework.response.status(200, package)

    def update(self, framework):
        data = framework.request.query("data", True)
        fs = framework.model("wizfs", module="wiz").use("wiz")
        fs.write("wiz.json", data)
        framework.response.status(200, True)

    def apply(self, framework):
        config = framework.model("config", module="wiz")

        # create config code
        configpy = config.build_config()
        wizconfigpy = config.build_wiz()

        # save config files
        fs = framework.model("wizfs", module="wiz").use("wiz")
        fs.write("config/config.py", configpy)
        fs.write("config/wiz.py", wizconfigpy)
        
        framework.response.status(200, True)

    def clean(self, framework):
        fs = framework.model("wizfs", module="wiz").use("wiz")
        fs.delete("public/templates")
        fs.delete("public/cache")
        fs.write("config/.cache", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        framework.response.status(200, True)