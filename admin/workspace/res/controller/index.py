import season

class Controller(season.interfaces.wiz.ctrl.admin.workspace.view):

    def __startup__(self, framework):
        super().__startup__(framework)

    def __default__(self, framework):
        self.css('editor.less')
        self.js('editor.js')
        
        fs = self.wiz.storage()
        if fs.isdir("resources") == False:
            fs.makedirs("resources")
        
        branchpath = self.wiz.branchpath()
        self.exportjs(target=[{"path": branchpath, "name": "resources"}])
        framework.response.render('editor.pug')