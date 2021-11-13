import season

class Controller(season.interfaces.wiz.ctrl.admin.package.view):

    def __startup__(self, framework):
        super().__startup__(framework)

    def __default__(self, framework):
        self.css('editor.less')
        self.js('editor.js')
        
        fs = self.wiz.storage()
        if fs.isdir("interfaces/model") == False:
            fs.makedirs("interfaces/model")

        branchpath = self.wiz.branchpath() + "/interfaces"
        self.exportjs(target=[{"path": branchpath, "name": "model"}])
        framework.response.render('editor.pug')