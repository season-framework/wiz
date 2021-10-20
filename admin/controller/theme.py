import season

class Controller(season.interfaces.wiz.admin.base):

    def __startup__(self, framework):
        super().__startup__(framework)

    def __default__(self, framework):
        response = framework.response
        return response.redirect('/wiz/admin/theme/list')

    def list(self, framework):
        self.css('css/theme/list.less')
        self.js('js/theme/list.js')
        return framework.response.render('theme/list.pug')
