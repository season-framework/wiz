import season

class Controller(season.interfaces.wiz.ctrl.admin.framework.view):

    def __startup__(self, framework):
        super().__startup__(framework)

    def __default__(self, framework):
        framework.response.redirect('model')

    def res(self, framework):
        self.css('editor.less')
        self.js('editor.js')
        self.exportjs(target=[{"path": ".", "name": "resources"}])
        framework.response.render('editor.pug')

    def interfaces(self, framework):
        self.css('editor.less')
        self.js('editor.js')
        self.exportjs(target=[{"path": "app", "name": "interfaces"}])
        framework.response.render('editor.pug')
        
    def model(self, framework):
        self.css('editor.less')
        self.js('editor.js')
        self.exportjs(target=[{"path": "app", "name": "model"}])
        framework.response.render('editor.pug')

    def library(self, framework):
        self.css('editor.less')
        self.js('editor.js')
        self.exportjs(target=[{"path": "app", "name": "lib"}])
        framework.response.render('editor.pug')