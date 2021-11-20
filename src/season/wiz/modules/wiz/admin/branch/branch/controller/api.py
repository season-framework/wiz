import season
import pymysql
import json
from werkzeug.exceptions import HTTPException

class Controller(season.interfaces.wiz.ctrl.admin.branch.api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def create(self, framework):
        branch = framework.request.query("branch", True)
        base = framework.request.query("base", "master")

        allowed = "qwertyuiopasdfghjklzxcvbnm-1234567890"
        for ns in branch:
            if ns not in allowed:
                raise Exception(f"only alphabet and number and -, _ in branch name")
        for ns in base:
            if ns not in allowed:
                raise Exception(f"only alphabet and number and -, _ in branch name")

        name = framework.request.query("name", None)
        email = framework.request.query("email", None)
        framework.wiz.workspace.checkout(branch=branch, base_branch=base, name=name, email=email, reload=True)
        framework.response.cookies.set("season-wiz-branch", branch)
        framework.response.status(200, True)

    def delete(self, framework):
        branch = framework.request.query("branch", True)
        remote = framework.request.query("remote", True)
        if remote == 'true': remote = True
        else: remote = False
        framework.wiz.workspace.delete(branch, remote)
        framework.response.status(200, True)

    def list(self, framework):
        branches = framework.wiz.workspace.branches(working=True, git=True, status=True)
        active_branch = []
        stale_branch = []
        
        for i in range(len(branches)):
            if branches[i]['working']:
                branches[i]['changed'] = framework.wiz.workspace.changed(branches[i]['name'])
                branches[i]['author'] = framework.wiz.workspace.author(branches[i]['name'])
                active_branch.append(branches[i])
            else:
                stale_branch.append(branches[i])

        merge = framework.wiz.workspace.merge()
        pull_request = merge.branches()
        for i in range(len(pull_request)):
            merge.checkout(pull_request[i]['from'], pull_request[i]['to'])
            pull_request[i]['author'] = merge.author()
        
        framework.response.status(200, active=active_branch, stale=stale_branch, pull_request=pull_request)

    def pull_request(self, framework):
        branch = framework.request.query("branch", True)
        base = framework.request.query("base_branch", True)
        name = framework.request.query("name", None)
        email = framework.request.query("email", None)

        fs = framework.model("wizfs", module="wiz").use(f"wiz/merge")
        if fs.isdir(f"{branch}_{base}"):
            framework.response.status(500, "merge request on working. please delete previous work.")    
    
        # branch: source branch, base_branch: apply changed
        framework.wiz.workspace.merge().checkout(branch, base, name=name, email=email)

        framework.response.status(200, True)
    
    def delete_request(self, framework):
        branch = framework.request.query("branch", True)
        base = framework.request.query("base_branch", True)
        merge = framework.wiz.workspace.merge().checkout(branch, base)
        merge.delete()
        framework.response.status(200, True)