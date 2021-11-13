import season

class view(season.interfaces.wiz.ctrl.base.view):
    def __startup__(self, framework):
        super().__startup__(framework)
        if len(self.config) == 0: framework.response.redirect("/wiz/install")
        if self.config.data.acl is not None: self.config.data.acl(framework)

        menus = self.config.get("topmenus", [])
        self.topnav(menus)
        
        menus = []
        menus.append({"title": "Packages", "url": '/wiz/admin/packages', 'pattern': r'^/wiz/admin/packages' })
        menus.append({"title": "Branch", "url": '/wiz/admin/branch', 'pattern': r'^/wiz/admin/branch' })
        menus.append({"title": "Setting", "url": '/wiz/admin/setting', 'pattern': r'^/wiz/admin/setting' })
        self.nav(menus)
    
class api(season.interfaces.wiz.ctrl.base.api):
    def __startup__(self, framework):
        super().__startup__(framework)
        if self.config.data.acl is not None: self.config.data.acl(framework)
