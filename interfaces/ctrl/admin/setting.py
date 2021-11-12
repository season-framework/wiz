import season

class view(season.interfaces.wiz.ctrl.admin.base.view):
    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('main.less')
        self.js('global.js')

        menus = []

        menus.append({"url": "/wiz/admin/setting/status", "icon": "fas fa-heartbeat", "title": "System Status", 'pattern': r'^/wiz/admin/setting/status'})
        menus.append({"url": "/wiz/admin/setting/configuration", "icon": "fas fa-cog", "title": "Configuration", 'pattern': r'^/wiz/admin/setting/configuration'})
        menus.append({"url": "/wiz/admin/setting/deploy", "icon": "fas fa-cloud-download-alt", "title": "Deploy & Backup"})
        menus.append({"url": "/wiz/admin/setting/restore", "icon": "fas fa-history", "title": "Restore"})
        menus.append({"url": "/wiz/admin/setting/cache_status", "icon": "fas fa-file-medical-alt", "title": "Cache Status"})
        
        # menus.append({"url": "/wiz/admin/setting/framework_general", "icon": "fas fa-rocket", "title": "Framework", 'pattern': r'^/wiz/admin/setting/framework', "sub": [
        #     {"url": "/wiz/admin/setting/framework_general", "icon": "fas fa-caret-right", "title": "Settings"},
        #     {"url": "/wiz/admin/setting/framework_handler/build", "icon": "fas fa-caret-right", "title": "Handler", 'pattern': r'^/wiz/admin/setting/framework_handler', 
        #         "sub": [
        #             {"url": "/wiz/admin/setting/framework_handler/build", "icon": "fas fa-caret-right", "title": "Build Handler"},
        #             {"url": "/wiz/admin/setting/framework_handler/filter", "icon": "fas fa-caret-right", "title": "Request Filter"},
        #             {"url": "/wiz/admin/setting/framework_handler/before_request", "icon": "fas fa-caret-right", "title": "Before Request Handler"},
        #             {"url": "/wiz/admin/setting/framework_handler/after_request", "icon": "fas fa-caret-right", "title": "After Request Handler"},
        #             {"url": "/wiz/admin/setting/framework_handler/error", "icon": "fas fa-caret-right", "title": "Error Handler"},
        #             {"url": "/wiz/admin/setting/framework_handler/resource", "icon": "fas fa-caret-right", "title": "Resource Handler"}
        #         ]
        #     },
        #     {"url": "/wiz/admin/setting/framework_config", "icon": "fas fa-caret-right", "title": "Config Files"},
        #     {"url": "/wiz/admin/setting/framework_lib", "icon": "fas fa-caret-right", "title": "Library"},
        #     {"url": "/wiz/admin/setting/framework_dic", "icon": "fas fa-caret-right", "title": "Dictionary"}
        # ]})

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
