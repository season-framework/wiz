import season
import time

WIZ_CONTROLLER = """### wiz.request.query(<KEY>, <DEFAULT_VALUE>)
# data = wiz.request.query() # get all queries as dict type
# value = wiz.request.query("key", "test") # get `key` value, if not exist in query, return default value
# value = wiz.request.query("key", True) # if default value is True, this key required

### load text from dictionary
# hello = dic("hello")
# title = dic("title.text")

### use selected controller
# controller.custom_function()

### use segments
### Route: /board/<category>/list
### View URI: /board/notice/list
# segment = framework.request.segment

### render app
# wiz.response.render("main")
# wiz.response.render("app_namespace")
# wiz.response.render("<url_pattern_1>", "<app_namespace>", key="value", key2="value2")
# wiz.response.render("<url_pattern_2>", "<app_namespace>", key="value", key2="value3")
# wiz.response.status(200)
"""

class Controller(season.interfaces.wiz.ctrl.admin.workspace.view):

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
        self.js('/wiz/theme/editor/editor.js')
        self.css('editor.css')

        app_id = framework.request.segment.get(0, True)
        info = self.wiz.data.get(app_id, mode='route')

        if info is None:
            pkg = dict()
            pkg["id"] = framework.lib.util.randomstring(12) + str(int(time.time()))
            pkg["title"] = "New Route"
            pkg["namespace"] = pkg["id"]
            pkg["route"] = ""
            pkg["viewuri"] = ""

            info = dict()
            info["package"] = pkg
            info["controller"] = WIZ_CONTROLLER
            info["dic"] = dict()
            info["dic"]["default"] = dict()
            info["dic"]["default"]["hello"] = "hello"
            info["dic"]["ko"] = dict()
            info["dic"]["ko"]["hello"] = "안녕하세요"

            self.wiz.data.update(info, mode='route')
            framework.response.redirect("editor/" + pkg["id"])

        controllers = framework.wiz.controllers()
        self.exportjs(APPID=app_id, CTRLS=controllers)
        framework.response.render('editor.pug')
