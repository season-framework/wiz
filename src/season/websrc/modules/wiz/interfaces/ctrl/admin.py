import season

class view(season.interfaces.wiz.ctrl.base.view):
    def __startup__(self, framework):
        super().__startup__(framework)
        
        if len(self.config.data) == 0: framework.response.redirect("/wiz/install")
        if self.config.data.acl is not None: self.config.data.acl(framework)

        menus = list(self.config.get("topmenus", []))
        menus.append({"title": "Setting", "url": '/wiz/admin/setting', 'pattern': r'^/wiz/admin/setting' })
        self.topnav(menus)
        
        menus = []
        menus.append({"title": "Workspace", "url": '/wiz/admin/workspace', 'pattern': r'^/wiz/admin/workspace' })
        menus.append({"title": "Branch", "url": '/wiz/admin/branch', 'pattern': r'^/wiz/admin/branch' })
        self.nav(menus)

        category = self.config.get("category")
        IS_DEV = framework.wiz.is_dev()
        branch = framework.wiz.workspace.branch()
        branches = framework.wiz.workspace.branches()
        self.exportjs(CATEGORIES=category, BRANCH=branch, BRANCHES=branches, IS_DEV=IS_DEV)
        framework.response.data.set(branches=branches, IS_DEV=IS_DEV)

        self.plugin = framework.model("plugin", module="wiz")
    
class api(season.interfaces.wiz.ctrl.base.api):
    def __startup__(self, framework):
        super().__startup__(framework)
        if self.config.data.acl is not None: self.config.data.acl(framework)
        self.plugin = framework.model("plugin", module="wiz")