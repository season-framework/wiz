import season

class base(season.interfaces.wiz.controller.base):
    def __startup__(self, framework):
        super().__startup__(framework)
        if self.config.acl is not None: self.config.acl(framework)

        if 'topmenus' in self.config: self.topnav(self.config.topmenus)
        
        menus = []
        menus.append({"title": "Interfaces", "url": '/wiz/admin/list', 'pattern': r'^/wiz/admin/list' })
        # menus.append({"title": "Theme", "url": '/wiz/admin/theme', 'pattern': r'^/wiz/admin/theme' })
        menus.append({"title": "Model", "url": '/wiz/admin/model', 'pattern': r'^/wiz/admin/model' })
        menus.append({"title": "Resources", "url": '/wiz/admin/res', 'pattern': r'^/wiz/admin/res' })
        self.nav(menus)
    
class api(base):
    def __startup__(self, framework):
        super().__startup__(framework)

    def __error__(self, framework, e):
        framework.response.json({"status": 500, "error": str(e)})
