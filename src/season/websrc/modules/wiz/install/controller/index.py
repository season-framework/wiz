import season
import json
from werkzeug.exceptions import HTTPException

class Controller(season.interfaces.wiz.ctrl.base.view):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.framework = framework

    def __default__(self, framework):
        if len(self.config.data) > 0: framework.response.redirect("/wiz")
        model = framework.model("plugin", module="wiz")
        model.build()
        plugin = model.instance("core.setting")
        plugin.layout('core.theme.layout', navbar=False, monaco=True)
        plugin.render("core.setting.installer")
        
    def build(self, framework):
        if len(self.config.data) > 0: framework.response.status(403)
        
        data = framework.request.query("data", True)
        fs = framework.model("wizfs", module="wiz").use("wiz")
        fs.write("wiz.json", data)
        
        config = framework.model("config", module="wiz")

        # create config code
        configpy = config.build_config()
        wizconfigpy = config.build_wiz()

        # save config files
        fs = framework.model("wizfs", module="wiz").use("wiz")
        fs.write("config/config.py", configpy)
        fs.write("config/wiz.py", wizconfigpy)
        
        framework.response.status(200)
