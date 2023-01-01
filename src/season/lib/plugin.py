import os
import season
import git

class Plugin:
    def __init__(self, path):
        self.path = season.util.std.stdClass()
        self.path.project = path
        self.path.ide = os.path.join(path, "ide")
        self.path.plugin = os.path.join(path, "plugin")
        self.path.cache = os.path.join(path, ".wiz.cache")
        self.path.lib = season.PATH_LIB

        self.fs = season.util.std.stdClass()
        self.fs.project = season.util.os.FileSystem(self.path.project)
        self.fs.ide = season.util.os.FileSystem(self.path.ide)
        self.fs.plugin = season.util.os.FileSystem(self.path.plugin)
        self.fs.cache = season.util.os.FileSystem(self.path.cache)
        self.fs.lib = season.util.os.FileSystem(self.path.lib)

    def add(self, uri):
        pluginfs = self.fs.plugin
        cachefs = self.fs.cache
        libfs = self.fs.lib

        cachefs.delete()
        cachefs.makedirs()
    
        if uri[:4] == "http":    
            git.Repo.clone_from(uri, cachefs.abspath("plugin"))
            plugininfo = cachefs.read.json(os.path.join("plugin", "plugin.json"))
            plugin_id = plugininfo["package"]
            if pluginfs.exists(plugin_id):
                cachefs.delete()
                raise Exception(f"plugin '{plugin_id}' already exists")
            cachefs.move("plugin", pluginfs.abspath(plugin_id))
            cachefs.delete()
            return plugin_id
        
        if pluginfs.exists(uri):
            cachefs.delete()
            raise Exception(f"plugin '{uri}' already exists")

        if libfs.exists(os.path.join("data", "plugin", uri)):
            pluginfs.copy(libfs.abspath(os.path.join("data", "plugin", uri)), uri)
            cachefs.delete()
            return uri
        
        raise Exception(f"plugin '{uri}' not found")

    def install(self, uri):
        self.add(uri)

    def remove(self, plugin_id):
        pluginfs = self.fs.plugin
        plugininfo = pluginfs.read.json(os.path.join(plugin_id, "plugin.json"))
        if plugininfo is None:
            raise Exception(f"plugin '{plugin_id}' not found")
        pluginfs.delete(plugin_id)

    def uninstall(self, plugin_id):
        self.remove(plugin_id)

    def upgrade(self, plugin_id):
        pluginfs = self.fs.plugin
        cachefs = self.fs.cache

        plugininfo = pluginfs.read.json(os.path.join(plugin_id, "plugin.json"))
        if plugininfo is None:
            raise Exception(f"plugin '{plugin_id}' not found")

        repo = plugininfo['repo']
        pluginfs.delete(plugin_id)
        self.add(repo)
