import season

class Controller(season.interfaces.wiz.ctrl.admin.setting.view):

    def __startup__(self, framework):
        super().__startup__(framework)
        
    def __default__(self, framework):
        framework.response.redirect('status')
