import season

class view(season.interfaces.wiz.ctrl.admin.base.view):
    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('main.less')
        self.js('global.js')

        menus = []

        menus.append({"url": "/wiz/admin/setting/status", "icon": "fas fa-heartbeat", "title": "System Status", 'pattern': r'^/wiz/admin/setting/status'})
        menus.append({"url": "/wiz/admin/setting/configuration", "icon": "fas fa-cog", "title": "Configuration", 'pattern': r'^/wiz/admin/setting/configuration'})
        menus.append({"url": "/wiz/admin/setting/acl", "icon": "fas fa-shield-alt", "title": "Access control", 'pattern': r'^/wiz/admin/setting/acl'})
        menus.append({"url": "/wiz/admin/setting/onerror", "icon": "fas fa-exclamation-triangle", "title": "On error", 'pattern': r'^/wiz/admin/setting/onerror'})
        menus.append({"url": "/wiz/admin/setting/onboot", "icon": "fas fa-power-off", "title": "On boot", 'pattern': r'^/wiz/admin/setting/onboot'})
        menus.append({"url": "/wiz/admin/setting/build_resource", "icon": "fas fa-filter", "title": "Build resource", 'pattern': r'^/wiz/admin/setting/build_resource'})
        menus.append({"url": "/wiz/admin/setting/after_request", "icon": "fas fa-filter", "title": "After Request", 'pattern': r'^/wiz/admin/setting/after_request'})

        self.setting_nav(menus)

    def setting_nav(self, menus):
        framework = self.framework

        def itermenu(menu):
            pt = None
            if 'pattern' in menu: pt = menu['pattern']
            elif 'url' in menu: pt = menu['url']
            if pt is not None:
                if framework.request.match(pt): menu['class'] = 'active'
                else: menu['class'] = ''
            
            if 'sub' in menu:
                for sub in menu['sub']:
                    itermenu(sub)

        for menu in menus:
            itermenu(menu)

        framework.response.data.set(settingmenus=menus)

class api(season.interfaces.wiz.ctrl.admin.base.api):
    def __startup__(self, framework):
        super().__startup__(framework)
