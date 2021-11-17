import season

class Controller(season.interfaces.wiz.ctrl.admin.branch.view):

    def __startup__(self, framework):
        super().__startup__(framework)

    def __default__(self, framework):
        framework.response.redirect('list')

    def list(self, framework):
        branches = framework.wiz.workspace.branches(working=True, git=True, status=True)
        for i in range(len(branches)):
            if branches[i]['working']:
                changed = framework.wiz.workspace.changed(branches[i]['name'])
                branches[i]['changed'] = len(changed)

        self.js('list.js')
        self.exportjs(branches=branches)
        framework.response.render('list.pug')