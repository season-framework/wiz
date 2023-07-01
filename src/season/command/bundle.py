import season
import os
from argh import arg

@arg('--project', default='main', help='project name')
def bundle(project="main"):
    fs = season.util.os.FileSystem(os.getcwd())
    BUNDLE_PATH = os.path.join("branch", project, "bundle")
    if fs.isdir(BUNDLE_PATH) == False:
        print("project '{}' not exists".format(project))
        return

    fs.makedirs("bundle")
    fs.remove("bundle/project")
    fs.remove("bundle/config")
    fs.remove("bundle/public")
    fs.makedirs("bundle/project")
    fs.makedirs("bundle/config")
    fs.makedirs("bundle/public")

    fs.copy(BUNDLE_PATH, "bundle/project")
    fs.copy("config", "bundle/config")
    fs.copy("public", "bundle/public")
