import season

class Controller(season.interfaces.wiz.admin.base):

    def __startup__(self, framework):
        super().__startup__(framework)

    def __default__(self, framework):
        response = framework.response
        return response.redirect('list')

    def res(self, framework):
        self.css('css/editor.less')
        self.js('js/editor.js')
        self.exportjs(target=[{"path": ".", "name": "resources"}])
        return framework.response.render('editor.pug')

    def model(self, framework):
        self.css('css/editor.less')
        self.js('js/editor.js')
        self.exportjs(target=[{"path": "app", "name": "interfaces"}, {"path": "app", "name": "model"}])
        return framework.response.render('editor.pug')

    def system(self, framework):
        self.css('css/editor.less')
        self.js('js/editor.js')
        target = []
        target.append({"path": "_system", "name": "config", "display": "System Config"})
        target.append({"path": "app", "name": "config", "display": "Framework Config"})
        self.exportjs(target=target)

        is_dev = self.wiz.is_dev()
        return framework.response.render('editor.pug', is_dev=is_dev)
