import season
import time

WIZ_CONTROLLER = """# use framework controller
# controller = season.interfaces.controller.admin.view()
# controller.__startup__(framework)

# TODO: Setup Access Level
if 'id' not in framework.session:
    framework.response.abort(401)

# use segments
# Route: /board/<category>/list
# View URI: /board/notice/list
segment = framework.request.segment
framework.log(segment)

# TODO: Build view variables
kwargs['message'] = "Hello, World!"
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

            self.wiz.data.update(info, mode='route')
            framework.response.redirect("editor/" + pkg["id"])

        controllers = framework.wiz.controllers()
        self.exportjs(APPID=app_id, CTRLS=controllers)
        framework.response.render('editor.pug')
