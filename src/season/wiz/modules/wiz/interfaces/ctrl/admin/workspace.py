import season

class view(season.interfaces.wiz.ctrl.admin.base.view):
    def __startup__(self, framework):
        super().__startup__(framework)

        menus = []
        menus.append({"title":"Route", "url": '/wiz/admin/workspace/routes', 'pattern': r'^/wiz/admin/workspace/routes' })
        menus.append({"title":"App", "url": '/wiz/admin/workspace/apps', 'pattern': r'^/wiz/admin/workspace/apps' })
        menus.append({"title":"Controller", "url": '/wiz/admin/workspace/ctrls', 'pattern': r'^/wiz/admin/workspace/ctrls' })
        menus.append({"title":"Model", "url": '/wiz/admin/workspace/models', 'pattern': r'^/wiz/admin/workspace/models' })
        menus.append({"title":"Theme", "url": '/wiz/admin/workspace/themes', 'pattern': r'^/wiz/admin/workspace/themes' })
        menus.append({"title":"Resource", "url": '/wiz/admin/workspace/res', 'pattern': r'^/wiz/admin/workspace/res' })
        menus.append({"title":"Config", "url": '/wiz/admin/workspace/config', 'pattern': r'^/wiz/admin/workspace/config' })
        self.subnav(menus)

class api(season.interfaces.wiz.ctrl.admin.base.api):
    def __startup__(self, framework):
        super().__startup__(framework)
