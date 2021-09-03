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
        self.js('js/list.js')
        search = framework.request.query()
        self.exportjs(search=search, session=framework.session)
        return framework.response.render('list.pug')

    def editor(self, framework):
        self.js('js/editor.js')
        self.css('css/editor.css')
        
        app_id = framework.request.segment.get(0, True)
        info = self.db.get(id=app_id)

        if info is None:
            info = dict()
            info["title"] = "새로운 위젯"
            info["user_id"] = framework.session['id']
            newid = framework.lib.util.randomstring(32)
            res = self.db.get(id=newid)
            while res is not None:
                newid = framework.lib.util.randomstring(32)
                res = self.db.get(id=newid)
            info["id"] = newid
            info["namespace"] = newid
            info["created"] = datetime.datetime.now()
            self.db.insert(info)
            framework.response.redirect("editor/" + newid)
        
        self.exportjs(app_id=app_id)
        framework.response.render('editor.pug')
