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
        framework.response.status(200, active=active_branch, stale=stale_branch)

    def merge(self, framework):
        branch = framework.request.query("branch", True)
        base = framework.request.query("base", "master")
        name = framework.request.query("name", None)
        email = framework.request.query("email", None)
        
        # branch: apply changed, base_branch: source branch
        framework.wiz.workspace.checkout(branch=branch, base_branch=base, name=name, email=email, reload=True)
        framework.response.cookies.set("season-wiz-branch", branch)
        framework.response.status(200, True)