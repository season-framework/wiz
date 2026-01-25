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

@arg('projectname', default='sample-project', help='project name')
def create(projectname):
    PATH_PROJECT = os.path.join(os.getcwd(), projectname)
    if os.path.isdir(PATH_PROJECT):
        print("Already exists project path '{}'".format(PATH_PROJECT))
        return
    
    fs = season.util.fs(PATH_PROJECT)

    print("create project...")
    PATH_PUBLIC_SRC = os.path.join(PATH_FRAMEWORK, 'data', "websrc")
    fs.copy(PATH_PUBLIC_SRC, PATH_PROJECT)

    startport = 3000
    while portchecker(startport):
        startport = startport + 1
    
    data = fs.read(os.path.join('config', 'boot.py'))
    data = data.replace("__PORT__", str(startport))
    fs.write(os.path.join('config', 'boot.py'), data)

    print("install ide...")
    fs.copy(os.path.join(PATH_FRAMEWORK, 'data', "ide"), "ide")
    fs.copy(os.path.join(PATH_FRAMEWORK, 'data', "plugin"), "plugin")

    fs.makedirs(os.path.join(PATH_PROJECT, "project"))
    
    print("build ide...")
    app = season.server(PATH_PROJECT)
    wiz = app.wiz()
    wiz.ide.build.clean()
    wiz.ide.build()

    