import season
import os
from argh import arg
import socket

PATH_FRAMEWORK = os.path.dirname(os.path.dirname(__file__))
frameworkfs = season.util.fs(PATH_FRAMEWORK)

def portchecker(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        port = int(port)
        s.connect(("127.0.0.1", port))
        return True
    except:
        pass
    return False

@arg('projectname', nargs='?', default=None, help='project name')
def create(projectname):
    """
    Create a new WIZ workspace
    
    Usage:
        wiz create <projectname>    - Create new workspace with given name
    
    Example:
        wiz create myapp            - Creates 'myapp' workspace
    """
    if projectname is None:
        print("Project name is required.")
        print("")
        print("Usage:")
        print("  wiz create <projectname>    - Create new workspace")
        print("")
        print("Example:")
        print("  wiz create myapp            - Creates 'myapp' workspace")
        return
    
    PATH_PROJECT = os.path.join(os.getcwd(), projectname)
    if os.path.isdir(PATH_PROJECT):
        print(f"Already exists project path '{PATH_PROJECT}'")
        return
    
    try:
        fs = season.util.fs(PATH_PROJECT)

        print("Creating workspace...")
        PATH_PUBLIC_SRC = os.path.join(PATH_FRAMEWORK, 'data', "websrc")
        fs.copy(PATH_PUBLIC_SRC, PATH_PROJECT)

        startport = 3000
        while portchecker(startport):
            startport = startport + 1
        
        data = fs.read(os.path.join('config', 'boot.py'))
        data = data.replace("__PORT__", str(startport))
        fs.write(os.path.join('config', 'boot.py'), data)

        print("Installing IDE...")
        fs.copy(os.path.join(PATH_FRAMEWORK, 'data', "ide"), "ide")
        fs.copy(os.path.join(PATH_FRAMEWORK, 'data', "plugin"), "plugin")

        fs.makedirs(os.path.join(PATH_PROJECT, "project"))
        
        print("Building IDE...")
        app = season.server(PATH_PROJECT)
        wiz = app.wiz()
        wiz.ide.build.clean()
        wiz.ide.build()

        print(f"Workspace '{projectname}' created successfully.")
        print(f"  Path: {PATH_PROJECT}")
        print(f"  Port: {startport}")
        print("")
        print("To start the server:")
        print(f"  cd {projectname}")
        print(f"  wiz run")
    except Exception as e:
        print(f"Create failed: {e}")

    