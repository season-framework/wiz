import season
import os
from argh import arg

@arg('action', default=None, help="add|remove|upgrade")
def plugin(action, *args):
    fs = season.util.filesystem(os.getcwd())

    if fs.exists(os.path.join("public", "app.py")) == False:
        print("Invalid Project path: wiz structure not found in this folder.")
        return

    class Command:
        def __call__(self, name, args):
            app = season.app(path=os.getcwd())
            wiz = app.wiz()
            
            for arg in args:
                try:
                    print(f"{name} `{arg}`...")
                    plugin = season.plugin(os.getcwd())
                    fn = getattr(plugin, name)
                    fn(arg)
                    print(f"{name} `{arg}` finished")
                except Exception as e:
                    print(e)
            wiz.ide.build()

    cmd = Command()
    cmd(action, args)

@arg('plugin', default=None, help="workspace")
@arg('command', default=None, help="build")
def command(plugin, command, *args):
    app = season.server(os.getcwd())
    wiz = app.wiz()
    plugin = wiz.ide.plugin = wiz.ide.plugin(plugin)
    cmd = plugin.command(command)
    cmd(*args)

