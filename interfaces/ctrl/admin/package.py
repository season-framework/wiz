import season

class view(season.interfaces.wiz.ctrl.admin.base.view):
    def __startup__(self, framework):
        super().__startup__(framework)

        menus = []
        menus.append({"title":"Route", "url": '/wiz/admin/packages/routes', 'pattern': r'^/wiz/admin/packages/routes' })
        menus.append({"title":"App", "url": '/wiz/admin/packages/apps', 'pattern': r'^/wiz/admin/packages/apps' })
        menus.append({"title":"Controller", "url": '/wiz/admin/packages/ctrls', 'pattern': r'^/wiz/admin/packages/ctrls' })
        menus.append({"title":"Model", "url": '/wiz/admin/packages/models', 'pattern': r'^/wiz/admin/packages/models' })
        menus.append({"title":"Theme", "url": '/wiz/admin/packages/themes', 'pattern': r'^/wiz/admin/packages/themes' })
        menus.append({"title":"Resource", "url": '/wiz/admin/packages/res', 'pattern': r'^/wiz/admin/packages/res' })
        self.subnav(menus)

class api(season.interfaces.wiz.ctrl.admin.base.api):
    def __startup__(self, framework):
        super().__startup__(framework)
