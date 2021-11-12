import season

class view(season.interfaces.wiz.ctrl.base.view):
    def __startup__(self, framework):
        super().__startup__(framework)
        if len(self.config) == 0: framework.response.redirect("/wiz/install")
        if self.config.data.acl is not None: self.config.data.acl(framework)

        menus = self.config.get("topmenus", [])
        self.topnav(menus)
        
        menus = []
        menus.append({"title": "Routes", "url": '/wiz/admin/routes', 'pattern': r'^/wiz/admin/routes' })
        menus.append({"title": "Apps", "url": '/wiz/admin/apps', 'pattern': r'^/wiz/admin/apps' })
        menus.append({"title": "Themes", "url": '/wiz/admin/themes', 'pattern': r'^/wiz/admin/themes' })
        menus.append({"title": "Framework", "url": '/wiz/admin/framework', 'pattern': r'^/wiz/admin/framework' })
        menus.append({"title": "Setting", "url": '/wiz/admin/setting', 'pattern': r'^/wiz/admin/setting' })
        self.nav(menus)
    
class api(season.interfaces.wiz.ctrl.base.api):
    def __startup__(self, framework):
        super().__startup__(framework)
        if self.config.data.acl is not None: self.config.data.acl(framework)
