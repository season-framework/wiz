import season
import os
from argh import arg

@arg('action', default=None, help="install | remove | upgrade | build")
def ide(action, *args):
    PATH_FRAMEWORK = os.path.dirname(os.path.dirname(__file__))
    frameworkfs = season.util.fs(PATH_FRAMEWORK)
    fs = season.util.fs(os.getcwd())
    idefs = season.util.fs(os.path.join(os.getcwd(), "ide"))
    pluginfs = season.util.fs(os.path.join(os.getcwd(), "plugin"))
    cachefs = season.util.fs(os.path.join(os.getcwd(), ".wiz.cache"))

    if fs.exists(os.path.join("public", "app.py")) == False:
        print("Invalid Project path: wiz structure not found in this folder.")
        return

    app = season.server(os.getcwd())
    wiz = app.wiz()

    class Command:
        def install(self):
            if idefs.exists():
                print("WIZ IDE Already Installed")
                return False

            print("installing WIZ IDE...")
            fs.copy(frameworkfs.abspath(os.path.join("data", "ide")), "ide")
            
            if pluginfs.exists() == False:
                fs.copy(frameworkfs.abspath(os.path.join("data", "plugin")), "plugin")

            wiz.ide.build.clean()
            wiz.ide.build()
            print("WIZ IDE installed")
            return True

        def remove(self):
            if idefs.exists() == False:
                print("WIZ IDE is not installed")
                return False
            idefs.remove()
            print("WIZ IDE removed")
            return True

        def upgrade(self, *args):
            print("Upgrading WIZ IDE...")
            idefs.remove()
            pluginfs.remove()

            fs.copy(frameworkfs.abspath(os.path.join("data", "ide")), "ide")
            fs.copy(frameworkfs.abspath(os.path.join("data", "plugin")), "plugin")
                
            wiz.ide.build.clean()
            wiz.ide.build()

            print("WIZ IDE upgraded")

        def build(self):
            if idefs.exists() == False:
                print("WIZ IDE is not installed")
                return False
            wiz.ide.build()

        def clean(self):
            if idefs.exists() == False:
                print("WIZ IDE is not installed")
                return False
            wiz.ide.build.clean()
            
        def __call__(self, name, args):
            cachefs.delete()
            cachefs.makedirs()
            fn = getattr(self, name)
            fn(*args)
            cachefs.delete()

    cmd = Command()
    cmd(action, args)
    