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
        if fs.exists("public", "app.py") == False:
            print("Invalid Project path: wiz structure not found in this folder.")
            return

        if idefs.exists():
            print("WIZ IDE Already Installed")
            return False

        fs.copy(frameworkfs.abspath("data", "ide"), "ide")
        
        if pluginfs.exists() == False:
            fs.copy(frameworkfs.abspath("data", "plugin"), "plugin")

        workspace.build.clean()
        workspace.build()
        return True

    def remove(self):
        if fs.exists("public", "app.py") == False:
            print("Invalid Project path: wiz structure not found in this folder.")
            return

        if idefs.exists() == False:
            print("WIZ IDE is not installed")
            return False

        idefs.remove()
        print("WIZ IDE removed")
        return True

    def upgrade(self):
        if fs.exists("public", "app.py") == False:
            print("Invalid Project path: wiz structure not found in this folder.")
            return
        
        print("Installing WIZ IDE...")
        idefs.remove()
        fs.copy(frameworkfs.abspath("data", "ide"), "ide")
        workspace.build.clean()
        workspace.build()

    def build(self):
        if fs.exists("public", "app.py") == False:
            print("Invalid Project path: wiz structure not found in this folder.")
            return

        if idefs.exists() == False:
            print("WIZ IDE is not installed")
            return False

        workspace.build()
        
    def __call__(self, name, args):
        if idefs.exists() == False:
            print("Not WIZ Project Directory")
            return

        cachefs.delete()
        cachefs.makedirs()
        try:
            fn = getattr(self, name)
            fn(*args)
        except:
            pass
        cachefs.delete()

@arg('action', default=None, help="add|remove|upgrade")
def ide(action, *args):
    cmd = Command()
    cmd(action, args)
    