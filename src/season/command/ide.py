import season
import git
import os
from argh import arg, expects_obj
import socket
import datetime

PATH_FRAMEWORK = os.path.dirname(os.path.dirname(__file__))
frameworkfs = season.util.os.FileSystem(PATH_FRAMEWORK)
fs = season.util.os.FileSystem(os.getcwd())
idefs = season.util.os.FileSystem(os.path.join(os.getcwd(), "ide"))
pluginfs = season.util.os.FileSystem(os.path.join(os.getcwd(), "plugin"))
cachefs = season.util.os.FileSystem(os.path.join(os.getcwd(), ".wiz.cache"))

app = season.app(path=os.getcwd())
workspace = app.wiz().workspace("ide")

class Command:
    def install(self):
        if idefs.exists():
            print("WIZ IDE Already Installed")
            return False

        print("installing WIZ IDE...")
        fs.copy(frameworkfs.abspath(os.path.join("data", "ide")), "ide")
        
        if pluginfs.exists() == False:
            fs.copy(frameworkfs.abspath(os.path.join("data", "plugin")), "plugin")

        workspace.build.clean()
        workspace.build()
        print("WIZ IDE installed")
        return True

    def remove(self):
        if idefs.exists() == False:
            print("WIZ IDE is not installed")
            return False
        idefs.remove()
        print("WIZ IDE removed")
        return True

    def upgrade(self):
        print("Upgrading WIZ IDE...")
        idefs.remove()
        fs.copy(frameworkfs.abspath(os.path.join("data", "ide")), "ide")
        workspace.build.clean()
        workspace.build()

        plugin = season.plugin(os.getcwd())
        plugin.upgrade("core")
        plugin.upgrade("workspace")
        plugin.upgrade("git")
        plugin.upgrade("utility")
        plugin.upgrade("portal")
        
        workspace.build()
        print("WIZ IDE upgraded")

    def build(self):
        if idefs.exists() == False:
            print("WIZ IDE is not installed")
            return False
        workspace.build()
        
    def __call__(self, name, args):
        cachefs.delete()
        cachefs.makedirs()
        fn = getattr(self, name)
        fn(*args)
        cachefs.delete()

@arg('action', default=None, help="install | remove | upgrade | build")
def ide(action, *args):
    if fs.exists(os.path.join("public", "app.py")) == False:
        print("Invalid Project path: wiz structure not found in this folder.")
        return
    cmd = Command()
    cmd(action, args)
    