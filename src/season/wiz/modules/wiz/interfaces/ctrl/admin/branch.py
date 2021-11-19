import season

class view(season.interfaces.wiz.ctrl.admin.base.view):
    def __startup__(self, framework):
        super().__startup__(framework)        

        # menus = []
        # menus.append({"title":"Commits", "url": '/wiz/admin/branch/commits', 'pattern': r'^/wiz/admin/branch/commits' })
        # menus.append({"title":"Working Branch", "url": '/wiz/admin/branch/working', 'pattern': r'^/wiz/admin/branch/working' })
        # menus.append({"title":"Git Branch", "url": '/wiz/admin/branch/git', 'pattern': r'^/wiz/admin/branch/git' })
        # self.subnav(menus)

class api(season.interfaces.wiz.ctrl.admin.base.api):
    def __startup__(self, framework):
        super().__startup__(framework)
