import season
import datetime

class Controller(season.interfaces.wiz.controller.base):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('css/main.less')
        if self.config.acl is not None: self.config.acl(framework)

    def __default__(self, framework):
        response = framework.response
        return response.redirect('list')

    def list(self, framework):
        if 'topmenus' in self.config: self.topnav(self.config.topmenus)

        cate = framework.request.segment.get(0, None)
        self.js('js/list.js')
        search = framework.request.query()
        search['category'] = cate

        category = ['widget', 'page']
        try:
            category = self.config.category
        except:
            pass
        menus = []
        for c in category:
            menus.append({ 'title': c, 'url': f'/wiz/widget/list/{c}' , 'pattern': r'^/wiz/widget/list/' + c })
        if cate is None:
            return framework.response.redirect('list/' + category[0])
        
        self.nav(menus)

        self.exportjs(search=search)
        return framework.response.render('list.pug', category=cate)

    def editor(self, framework):
        self.js('js/editor.js')
        self.css('css/editor.css')
        
        app_id = framework.request.segment.get(0, True)
        info = self.db.get(id=app_id)

        category = ['widget', 'page']
        try:
            category = self.config.category
        except:
            pass
        cate = framework.request.query("category", category[0])

        if info is None:
            info = dict()
            info["title"] = "New Widget"
            info["category"] = cate
            try:
                info["user_id"] = self.config.uid(framework)
            except:
                info["user_id"] = "unknown"
            newid = framework.lib.util.randomstring(32)
            res = self.db.get(id=newid)
            while res is not None:
                newid = framework.lib.util.randomstring(32)
                res = self.db.get(id=newid)
            info["id"] = newid
            info["namespace"] = newid
            info["created"] = datetime.datetime.now()
            info["kwargs"] = ""
            info["html"] = ".container\n    h3 New Widget"
            info["js"] = "var wiz_controller = function ($sce, $scope, $timeout) {\n\n}" 
            info["css"] = ""
            info["api"] = 'def _status(framework, code, data):\n    res = dict()\n    res["code"] = code\n    res["data"] = data\n    framework.response.json(res)\n\ndef myfunc(framework):\n    _status(framework, 200, rows)'
            self.db.insert(info)
            framework.response.redirect("editor/" + newid)
        
        self.exportjs(app_id=app_id, category=category)
        framework.response.render('editor.pug', category=category)
