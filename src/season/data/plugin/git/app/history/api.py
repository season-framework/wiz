import git
import os

workspace = wiz.workspace("service")

def history():
    cwd = workspace.fs().abspath()
    repo = git.Repo.init(cwd)
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

    wiz.response.status(200, commits)