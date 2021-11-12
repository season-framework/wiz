import season

class view(season.interfaces.wiz.ctrl.admin.base.view):
    def __startup__(self, framework):
        super().__startup__(framework)

        menus = []
        menus.append({"title":"Handler", "url": '/wiz/admin/framework/handler', 'pattern': r'^/wiz/admin/framework/handler' })
        menus.append({"title":"Interfaces", "url": '/wiz/admin/framework/interfaces', 'pattern': r'^/wiz/admin/framework/interfaces' })
        menus.append({"title":"Models", "url": '/wiz/admin/framework/model', 'pattern': r'^/wiz/admin/framework/model' })
        menus.append({"title":"Resources", "url": '/wiz/admin/framework/res', 'pattern': r'^/wiz/admin/framework/res' })
        menus.append({"title":"Library", "url": '/wiz/admin/framework/library', 'pattern': r'^/wiz/admin/framework/library' })
        self.subnav(menus)

class api(season.interfaces.wiz.ctrl.admin.base.api):
    def __startup__(self, framework):
        super().__startup__(framework)
