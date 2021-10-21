import season

class Controller(season.interfaces.wiz.admin.base):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('css/setting/main.less')
        self.js('js/setting/global.js')
        menus = []
        menus.append({"url": "/wiz/admin/setting/general", "icon": "fas fa-cog", "title": "General"})
        menus.append({"url": "/wiz/admin/setting/deploy", "icon": "fas fa-cloud-download-alt", "title": "Deploy & Backup"})
        menus.append({"url": "/wiz/admin/setting/restore", "icon": "fas fa-history", "title": "Restore"})
        menus.append({"url": "/wiz/admin/setting/cache_status", "icon": "fas fa-file-medical-alt", "title": "Cache Status"})
        self.setting_nav(menus)

    def __default__(self, framework):
        framework.response.redirect('/wiz/admin/setting/general')

    def general(self, framework):
        self.js('js/setting/general.js')
        framework.response.render('setting/general.pug', is_dev=self.wiz.is_dev())

    def deploy(self, framework):
        self.js('js/setting/deploy.js')
        framework.response.render('setting/deploy.pug')

    def restore(self, framework):
        self.js('js/setting/restore.js')
        framework.response.render('setting/restore.pug')

    def cache_status(self, framework):
        self.js('js/setting/cache.js')
        framework.response.render('setting/cache.pug')

    def setting_nav(self, menus):
        framework = self.__framework__

        for menu in menus:
            pt = None
            if 'pattern' in menu: pt = menu['pattern']
            elif 'url' in menu: pt = menu['url']

            if pt is not None:
                if framework.request.match(pt): menu['class'] = 'active'
                else: menu['class'] = ''

        framework.response.data.set(settingmenus=menus)