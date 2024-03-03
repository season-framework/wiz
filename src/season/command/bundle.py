import season
import os
from argh import arg

@arg('--project', default='main', help='project name')
def bundle(project="main"):
    fs = season.util.fs(os.getcwd())
    BUNDLE_PATH = os.path.join("project", project, "bundle")
    if fs.isdir(BUNDLE_PATH) == False:
        print("project '{}' not exists".format(project))
        return

    fs.remove("bundle")
    fs.makedirs("bundle")
    fs.makedirs("bundle/project/main/bundle")
    fs.makedirs("bundle/config")
    fs.makedirs("bundle/public")
    fs.makedirs("bundle/plugin")

    fs.copy(BUNDLE_PATH, "bundle/project/main/bundle")
    fs.copy("config", "bundle/config")
    fs.copy("public", "bundle/public")
    fs.copy("plugin", "bundle/plugin")
