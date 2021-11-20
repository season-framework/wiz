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
        merge = framework.wiz.workspace.merge()
        
        active_branches = merge.branches()
        branch = framework.request.segment.get(0, True)
        base_branch = framework.request.segment.get(1, True)
        active_branches = [h['from'] + "_" + h['to'] for h in active_branches]
        merge_path = branch + "_" + base_branch
        if merge_path not in active_branches:
            framework.response.redirect("/wiz/admin/branch")
        
        merge.checkout(branch, base_branch)
        author = merge.author()

        self.exportjs(author=author)
        self.exportjs(TARGET_BRANCH=merge_path)

        self.js('editor.js')
        self.css('editor.css')
        framework.response.render('editor.pug')