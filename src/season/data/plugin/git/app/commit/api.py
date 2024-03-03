import git
import os

cwd = wiz.project.fs().abspath()
repo = git.Repo.init(cwd)

def _history():
    branch = repo.active_branch.name
    
    try:
        commits = list(repo.iter_commits(branch, max_count=50, skip=0))
        for i in range(len(commits)):
            commits[i] = {
                "author": commits[i].author.name, 
                "author_email": commits[i].author.email, 
                "committer": commits[i].committer.name, 
                "committer_email": commits[i].committer.email, 
                "datetime": commits[i].committed_datetime, 
                "message": commits[i].message,
                "id": str(commits[i])
            }
    except Exception as e:
        commits = []
    return commits

def reset():
    gitfile = wiz.request.query("file", None)
    try:
        if gitfile is None or len(gitfile) == 0:
            repo.git.reset()
        else:
            repo.git.reset(gitfile)
    except:
        pass
    wiz.response.status(200)

def add():
    gitfile = wiz.request.query("file", None)
    try:
        if gitfile is None or len(gitfile) == 0:
            repo.git.add('--all')
        else:
            repo.git.add(gitfile, update=True)
    except:
        pass
    wiz.response.status(200)

def changes():
    res = dict(staged=[], unstaged=[])

    if len(_history()) == 0:
        wiz.response.status(200, res)

    try:
        tags = repo.commit('HEAD').diff(None)
        fmap = dict()
        for diff in tags:
            fmap[diff.b_path] = diff.change_type
    except:
        pass
    
    try:    
        staged = repo.index.diff("HEAD")
        for diff in staged:
            ctype = 'D'
            if diff.b_path in fmap: ctype = fmap[diff.b_path]
            obj = {"change_type": ctype, "path": diff.b_path}   
            path = obj['path']
            res['staged'].append(obj)
    except:
        pass

    try:
        unstaged = repo.index.diff(None)
        for diff in unstaged:
            ctype = 'D'
            if diff.b_path in fmap: ctype = fmap[diff.b_path]
            obj = {"change_type": ctype, "path": diff.b_path}
            path = obj['path']
            res['unstaged'].append(obj)
    except:
        pass

    wiz.response.status(200, res)

def commit():
    try:
        message = wiz.request.query("message", "commit")
        repo.index.commit(message)
    except Exception as e:
        wiz.response.status(500, str(e))
    wiz.response.status(200)