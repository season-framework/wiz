import season

class base(season.interfaces.wiz.controller.base):
    def __startup__(self, framework):
        super().__startup__(framework)
        if self.config.acl is not None: self.config.acl(framework)

        self.wiz = framework.model("wiz", module="wiz")

        menus = []
        if 'topmenus' in self.config:
            menus = list(self.config.topmenus)

        isdevmode = framework.request.query("devmode", None)
        if isdevmode is not None:
            is_dev = self.wiz.is_dev()
            if is_dev: self.wiz.set_dev("false")
            else: self.wiz.set_dev("true")
            framework.response.redirect("/wiz/admin/system")
        self.topnav(menus)
        
        menus = []
        menus.append({"title": "Interfaces", "url": '/wiz/admin/list', 'pattern': r'^/wiz/admin/list' })
        menus.append({"title": "Theme", "url": '/wiz/admin/theme', 'pattern': r'^/wiz/admin/theme' })
        menus.append({"title": "Model", "url": '/wiz/admin/model', 'pattern': r'^/wiz/admin/model' })
        menus.append({"title": "Resources", "url": '/wiz/admin/res', 'pattern': r'^/wiz/admin/res' })
        menus.append({"title": "System", "url": '/wiz/admin/system', 'pattern': r'^/wiz/admin/system' })
        self.nav(menus)
    
class api(base):
    def __startup__(self, framework):
        super().__startup__(framework)

    def __error__(self, framework, e):
        framework.response.json({"status": 500, "error": str(e)})
