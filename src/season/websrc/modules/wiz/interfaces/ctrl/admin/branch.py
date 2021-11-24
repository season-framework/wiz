import season

class view(season.interfaces.wiz.ctrl.admin.base.view):
    def __startup__(self, framework):
        super().__startup__(framework)        

class api(season.interfaces.wiz.ctrl.admin.base.api):
    def __startup__(self, framework):
        super().__startup__(framework)
