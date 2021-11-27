import season

class view(season.interfaces.wiz.ctrl.admin.setting.view):
    def __startup__(self, framework):
        super().__startup__(framework)
        self.plugin = framework.model("plugin", module="wiz")

class api(season.interfaces.wiz.ctrl.admin.setting.api):
    def __startup__(self, framework):
        super().__startup__(framework)
        self.plugin = framework.model("plugin", module="wiz")