import season
import time

class Controller(season.interfaces.wiz.ctrl.admin.plugin.view):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('main.less')
        
    def __default__(self, framework):
        framework.response.redirect("list")

    def list(self, framework):
        cate = framework.request.segment.get(0, None)
        self.js('list.js')
        framework.response.render('list.pug')

    def editor(self, framework):
        self.js('editor.js')
        self.css('editor.css')

        plugin_id = framework.request.segment.get(0, True)
        
        # info = self.wiz.data.get(app_id, mode='app')

        # if info is None:
        #     pkg = dict()
        #     pkg["id"] = framework.lib.util.randomstring(12) + str(int(time.time()))
        #     pkg["title"] = "New App"
        #     pkg["namespace"] = pkg["id"]
        #     pkg["properties"] = {"html": "pug", "js": "javascript", "css": "scss"}
        #     pkg["viewuri"] = ""

        #     info = dict()
        #     info["package"] = pkg
        #     info["controller"] = WIZ_CONTROLLER
        #     info["api"] = WIZ_API
        #     info["socketio"] = WIZ_SOCKET
        #     info["html"] = WIZ_PUG
        #     info["js"] = WIZ_JS
        #     info["css"] = ""
        #     info["dic"] = dict()
        #     info["dic"]["default"] = dict()
        #     info["dic"]["default"]["hello"] = "hello"
        #     info["dic"]["ko"] = dict()
        #     info["dic"]["ko"]["hello"] = "안녕하세요"

        #     self.wiz.data.update(info, mode='plugin')
        #     framework.response.redirect("editor/" + pkg["id"])
 
        self.exportjs(PLUGIN_ID=plugin_id)
        framework.response.render('editor.pug')

    def preview(self, framework):
        app_id = framework.request.segment.get(0, True)
        framework.request.segment = season.stdClass()
        wiz = framework.wiz.instance()
        wiz.response.render(app_id)
        framework.response.status(200, app_id)
