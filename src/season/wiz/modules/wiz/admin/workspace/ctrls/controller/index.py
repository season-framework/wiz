import season

class Controller(season.interfaces.wiz.ctrl.admin.workspace.view):

    def __startup__(self, framework):
        super().__startup__(framework)

    def __default__(self, framework):
        self.css('/wiz/theme/less/browser.less')
        self.js('browser.js')
        self.js('/wiz/theme/editor/browser.js')
        
        fs = self.wiz.storage()
        if fs.isdir("interfaces/controller") == False:
            fs.makedirs("interfaces/controller")

        branchpath = self.wiz.branchpath()
        self.exportjs(BRANCHPATH=branchpath)
        framework.response.render('browser.pug')