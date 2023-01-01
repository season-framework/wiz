import season
import git
import os
from argh import arg, expects_obj

fs = season.util.os.FileSystem(os.getcwd())
app = season.app(path=os.getcwd())
workspace = app.wiz().workspace("ide")

class Command:
    def __call__(self, name, args):
        for arg in args:
            try:
                print(f"{name} `{arg}`...")
                plugin = season.plugin(os.getcwd())
                fn = getattr(plugin, name)
                fn(arg)
                print(f"{name} `{arg}` finished")
            except Exception as e:
                print(e)
        workspace.build()

@arg('action', default=None, help="add|remove|upgrade")
def plugin(action, *args):
    if fs.exists(os.path.join("public", "app.py")) == False:
        print("Invalid Project path: wiz structure not found in this folder.")
        return
    cmd = Command()
    cmd(action, args)
    