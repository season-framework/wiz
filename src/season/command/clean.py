import os
import season
import git

def clean(*args, **kwargs):
    print("clean...")
    fs = season.util.os.FileSystem(season.path.project)
    fs.remove("cache")
    fs.remove("origin")

    print("init local remote git...")
    fs = season.util.os.FileSystem(os.path.join(season.path.project, 'branch'))
    srcfs = season.util.os.FileSystem(os.path.join(season.path.project, 'origin'))
    git.Repo.init(srcfs.abspath(), bare=True)
    branches = fs.use("branch").files()
    for branch in branches:
        repo = git.Repo.init(fs.abspath(branch))
        try:
            origin = repo.remote(name='wiz')
            repo.delete_remote(origin)
        except:
            pass
        origin = repo.create_remote('wiz', srcfs.abspath())
        origin.push(branch)
