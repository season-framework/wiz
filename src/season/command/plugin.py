import season
import git
import os
from argh import arg, expects_obj
import socket
import datetime

idefs = season.util.os.FileSystem(os.path.join(os.getcwd(), "ide"))
pluginfs = season.util.os.FileSystem(os.path.join(os.getcwd(), "plugin"))
cachefs = season.util.os.FileSystem(os.path.join(os.getcwd(), ".wiz.cache"))

app = season.app(path=os.getcwd())
workspace = app.wiz().workspace("ide")

class Command:

    def add(self, uri):
        print(f"download from {uri}...")
        git.Repo.clone_from(uri, cachefs.abspath("plugin"))
        plugininfo = cachefs.read.json(os.path.join("plugin", "plugin.json"))
        plugin_id = plugininfo["package"]
        if pluginfs.exists(plugin_id):
            print(f"plugin '{plugin_id}' already exists")
            return False
        cachefs.move("plugin", pluginfs.abspath(plugin_id))
        print(f"plugin `{plugin_id}` installed")
        return True

    def remove(self, plugin_id):
        plugininfo = pluginfs.read.json(os.path.join(plugin_id, "plugin.json"))
        if plugininfo is None:
            print(f"plugin '{plugin_id}' not found")
            return False
        pluginfs.delete(plugin_id)
        return True

    def upgrade(self, plugin_id):
        plugininfo = pluginfs.read.json(os.path.join(plugin_id, "plugin.json"))
        if plugininfo is None:
            print(f"plugin '{plugin_id}' not found")
            return False
        
        repo = plugininfo['repo']
        print(f"download from {repo}...")
        git.Repo.clone_from(repo, cachefs.abspath("plugin"))
        plugininfo = cachefs.read.json(os.path.join("plugin", "plugin.json"))
        plugin_new_id = plugininfo["package"]
        pluginfs.delete(plugin_id)
        cachefs.move("plugin", pluginfs.abspath(plugin_new_id))
        print(f"plugin `{plugin_new_id}` upgraded")
        return True
    
    def __call__(self, name, args):
        if idefs.exists() == False:
            print("Not WIZ Project Directory")
            return

        cachefs.delete()
        cachefs.makedirs()
        try:
            fn = getattr(self, name)
            stat = fn(*args)
            if stat:
                workspace.build()
        except:
            pass
        cachefs.delete()

@arg('action', default=None, help="add|remove|upgrade")
def plugin(action, *args):
    cmd = Command()
    cmd(action, args)
    