import season
import os
from argh import arg

@arg('action', nargs='?', default=None, help="install | remove | upgrade | build | clean")
def ide(action, *args):
    """
    WIZ IDE Management
    
    Usage:
        wiz ide install    - Install WIZ IDE
        wiz ide remove     - Remove WIZ IDE
        wiz ide upgrade    - Upgrade WIZ IDE
        wiz ide build      - Build WIZ IDE
        wiz ide clean      - Clean WIZ IDE cache
    """
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
        
        def help(self):
            print("WIZ IDE Management")
            print("")
            print("Usage:")
            print("  wiz ide install    - Install WIZ IDE")
            print("  wiz ide remove     - Remove WIZ IDE")
            print("  wiz ide upgrade    - Upgrade WIZ IDE")
            print("  wiz ide build      - Build WIZ IDE")
            print("  wiz ide clean      - Clean WIZ IDE cache")
            
        def __call__(self, name, args):
            cachefs.delete()
            cachefs.makedirs()
            fn = getattr(self, name)
            fn(*args)
            cachefs.delete()

    cmd = Command()
    
    # Show help if action is None or invalid
    if action is None:
        cmd.help()
        return
    
    if not hasattr(cmd, action):
        print(f"Unknown action: {action}")
        print("")
        cmd.help()
        return
    
    try:
        cmd(action, args)
    except Exception as e:
        print(f"Error: {e}")
        print("")
        cmd.help()
    