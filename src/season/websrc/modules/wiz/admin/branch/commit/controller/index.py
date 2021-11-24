import season

class Controller(season.interfaces.wiz.ctrl.admin.branch.view):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('main.less')

    def __error__(self, framework, err):
        framework.response.redirect("/wiz/admin/branch")

    def __default__(self, framework):
        framework.response.redirect("/wiz/admin/branch")
        
    def diff(self, framework):
        active_branches = framework.wiz.workspace.branches()
        branch = framework.request.segment.get(0, True)
        if branch not in active_branches:
            framework.response.redirect("/wiz/admin/branch")
        
        author = framework.wiz.workspace.author(branch)
        self.exportjs(author=author)

        self.exportjs(TARGET_BRANCH=branch)
        self.js('editor.js')
        self.css('editor.css')
        framework.response.render('editor.pug')