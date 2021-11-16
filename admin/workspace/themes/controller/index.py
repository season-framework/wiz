import os
import season
import shutil

class Controller(season.interfaces.wiz.ctrl.admin.workspace.view):

    def __startup__(self, framework):
        super().__startup__(framework)

    def __default__(self, framework):
        self.css('editor.less')
        self.js('editor.js')
        BASEPATH = self.wiz.branchpath()
        BASEPATH = os.path.join(BASEPATH, "themes")
        fs = framework.model("wizfs", module="wiz").use(BASEPATH)
        try:
            os.makedirs(fs.abspath("."))
        except:
            pass
        themes = fs.list()
        target = []
        for theme in themes:
            target.append({"path": BASEPATH, "name": theme})
        self.exportjs(target=target, BASEPATH=BASEPATH)
        return framework.response.render('editor.pug')
