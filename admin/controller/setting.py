import season
import sys

class Controller(season.interfaces.wiz.admin.base):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('css/setting/main.less')
        self.js('js/setting/global.js')
        menus = []
        menus.append({"url": "/wiz/admin/setting/general_status", "icon": "fas fa-cog", "title": "General", 'pattern': r'^/wiz/admin/setting/general', "sub": [
            {"url": "/wiz/admin/setting/general_status", "icon": "fas fa-caret-right", "title": "System Status"},
            {"url": "/wiz/admin/setting/general_framework", "icon": "fas fa-caret-right", "title": "Framework Setting"}
            # {"url": "/wiz/admin/setting/general_wiz", "icon": "fas fa-caret-right", "title": "WIZ Setting"}
        ]})
        menus.append({"url": "/wiz/admin/setting/deploy", "icon": "fas fa-cloud-download-alt", "title": "Deploy & Backup"})
        menus.append({"url": "/wiz/admin/setting/restore", "icon": "fas fa-history", "title": "Restore"})
        menus.append({"url": "/wiz/admin/setting/cache_status", "icon": "fas fa-file-medical-alt", "title": "Cache Status"})

        try:
            framework.response.data.set(SEASON_VERSION=season.version)
        except:
            framework.response.data.set(SEASON_VERSION="<= 0.3.8")
        framework.response.data.set(PYTHON_VERSION=sys.version)

        self.setting_nav(menus)

    def __default__(self, framework):
        framework.response.redirect('/wiz/admin/setting/general_status')


    def general_status(self, framework):
        self.js('js/setting/general/status.js')
        framework.response.render('setting/general/status.pug', is_dev=self.wiz.is_dev())

    def general_framework(self, framework):
        self.js('js/setting/general/framework.js')
        framework.response.render('setting/general/framework.pug', is_dev=self.wiz.is_dev())

    def general_wiz(self, framework):
        self.js('js/setting/general/wiz.js')
        framework.response.render('setting/general/wiz.pug', is_dev=self.wiz.is_dev())


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

            if 'sub' in menu:
                for sub in menu['sub']:
                    pt = None
                    if 'pattern' in sub: pt = sub['pattern']
                    elif 'url' in sub: pt = sub['url']

                    if pt is not None:
                        if framework.request.match(pt): sub['class'] = 'active'
                        else: sub['class'] = ''

        framework.response.data.set(settingmenus=menus)