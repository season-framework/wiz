import season
import git
import os
from argh import arg, expects_obj
import socket
import datetime

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
@arg('--uri', help='git project url')
@arg('--ide', help='git ide url')
def create(projectname, uri="https://github.com/season-framework/wiz-demo", ide="https://github.com/season-framework/wiz-ide"):
    PATH_FRAMEWORK = os.path.dirname(os.path.dirname(__file__))
    PATH_PROJECT = os.path.join(os.getcwd(), projectname)
    if os.path.isdir(PATH_PROJECT):
        return print("Already exists project path '{}'".format(PATH_PROJECT))
    
    fs = season.util.os.FileSystem(PATH_PROJECT)

    print("create project...")
    PATH_PUBLIC_SRC = os.path.join(PATH_FRAMEWORK, 'data')
    fs.copy(PATH_PUBLIC_SRC, PATH_PROJECT)

    startport = 3000
    while portchecker(startport):
        startport = startport + 1
    
    data = fs.read(os.path.join('config', 'server.py'))
    data = data.replace("__PORT__", str(startport))
    fs.write(os.path.join('config', 'server.py'), data)
    fs.write(os.path.join('config', 'installed.py'), "started = '" + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S') + "'")

    print("install ide...")
    git.Repo.clone_from(ide, fs.abspath("plugin"))

    print("install base branch...")
    repo = git.Repo.clone_from(uri, fs.abspath(os.path.join('branch', 'main')))
    branches = [h.name for h in repo.heads]
    if 'main' in branches:
        main = 'main'
    else:
        main = 'master'
    fs.move(fs.abspath(os.path.join('branch', 'main')), fs.abspath(os.path.join('branch', main)))