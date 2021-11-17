import season

class Controller(season.interfaces.wiz.ctrl.admin.branch.view):

    def __startup__(self, framework):
        super().__startup__(framework)

    def __default__(self, framework):
        framework.response.redirect('list')

    def list(self, framework):
        cate = framework.request.segment.get(0, None)
        self.js('list.js')
        framework.response.render('list.pug')