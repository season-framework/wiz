import season
import time

class Controller(season.interfaces.wiz.ctrl.admin.plugin.view):

    def __startup__(self, framework):
        super().__startup__(framework)
        
    def __default__(self, framework):
        framework.response.redirect("list")

    def list(self, framework):
        self.css('main.less')
        cate = framework.request.segment.get(0, None)
        self.js('list.js')
        framework.response.render('list.pug')

    def editor(self, framework):
        self.css('main.less')
        self.js('editor.js')
        self.css('editor.css')
        plugin_id = framework.request.segment.get(0, True)

        if self.plugin.get(plugin_id) is None:
            framework.response.redirect("list")

        self.exportjs(PLUGIN_ID=plugin_id)
        framework.response.render('editor.pug')

    def preview(self, framework):
        plugin_id = framework.request.segment.get(0, True)
        bundle_id = framework.request.segment.get(1, True)

        framework.request.segment = season.stdClass()
        plugin = self.plugin.instance(plugin_id)
        plugin.layout('core.theme.layout', navbar=False, monaco=True)
        plugin.render(bundle_id)

    def filebrowser(self, framework):
        self.css('browser.less')
        self.css('/wiz/theme/less/browser.less')
        self.js('browser.js')
        self.js('/wiz/theme/editor/browser.js')
        plugin_id = framework.request.segment.get(0, True)
        target = framework.request.segment.get(1, True)

        fs = framework.model("wizfs", module="wiz").use(f"wiz/plugin/{plugin_id}")
        if fs.isdir(target) == False:
            fs.makedirs(target)
        
        TARGET_PATH = fs.abspath()
        self.exportjs(TARGET_PATH=f"wiz/plugin/{plugin_id}", TARGET=target)
        framework.response.render('browser.pug')