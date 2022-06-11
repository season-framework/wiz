import season
import git
import os
from argh import arg, expects_obj
import datetime

@arg('target', default='ide', help='update ide from uri')
@arg('--uri', help='target uri')
def update(target, uri=None):
    # check wiz structure
    publicpath = os.path.join(season.path.project, 'public')
    apppath = os.path.join(publicpath, 'app.py')
    if os.path.isfile(apppath) == False:
        print("Invalid Project path: wiz structure not found in this folder.")
        return

    if target == 'ide':
        if uri is None: uri = "https://github.com/season-framework/wiz-ide"
        print(f"update ide from... {uri}")
        fs = season.util.os.FileSystem(season.path.project)
        fs.remove("plugin")
        fs.remove("cache")
        git.Repo.clone_from(uri, fs.abspath("plugin"))
