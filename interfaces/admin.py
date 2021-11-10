import season

class base(season.interfaces.wiz.controller.base):
    def __startup__(self, framework):
        super().__startup__(framework)
        if len(self.config) == 0: framework.response.redirect("/wiz/install")

        if self.config.acl is not None: self.config.acl(framework)

        self.wiz = framework.model("wiz", module="wiz")

        menus = []
        if 'topmenus' in self.config:
            menus = list(self.config.topmenus)
        self.topnav(menus)
        
        menus = []
        menus.append({"title": "Interfaces", "url": '/wiz/admin/list', 'pattern': r'^/wiz/admin/list' })
        menus.append({"title": "Theme", "url": '/wiz/admin/theme', 'pattern': r'^/wiz/admin/theme' })
        menus.append({"title": "Model", "url": '/wiz/admin/model', 'pattern': r'^/wiz/admin/model' })
        menus.append({"title": "Resources", "url": '/wiz/admin/res', 'pattern': r'^/wiz/admin/res' })
        menus.append({"title": "Setting", "url": '/wiz/admin/setting', 'pattern': r'^/wiz/admin/setting' })
        self.nav(menus)
    
class api(base):
    def __startup__(self, framework):
        super().__startup__(framework)

    def __error__(self, framework, e):
        framework.response.json({"status": 500, "error": str(e)})
