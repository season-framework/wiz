import season
import time

class Controller(season.interfaces.wiz.ctrl.admin.workspace.view):

    def __startup__(self, framework):
        super().__startup__(framework)
        
    def __default__(self, framework):
        self.css('logger.less')
        self.js('logger.js')
        BRANCH = framework.request.segment.get(0, framework.wiz.branch())
        self.exportjs(BRANCH=BRANCH)
        framework.response.render('logger.pug')
