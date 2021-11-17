import season

class Controller(season.interfaces.wiz.ctrl.admin.branch.view):

    def __startup__(self, framework):
        super().__startup__(framework)

    def __default__(self, framework):
        framework.response.redirect('list')

    def list(self, framework):
        branches = framework.wiz.workspace.branches(working=True, git=True, status=True)
        active_branch = []
        stale_branch = []
        for i in range(len(branches)):
            if branches[i]['working']:
                changed = framework.wiz.workspace.changed(branches[i]['name'])
                branches[i]['changed'] = len(changed)
                active_branch.append(branches[i])
            else:
                stale_branch.append(branches[i])

        self.js('list.js')
        self.exportjs(active_branch=active_branch, stale_branch=stale_branch)
        framework.response.render('list.pug')