import os
import shutil
from argh import arg, expects_obj
from git import Repo
import socket

def portchecker(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        port = int(port)
        s.connect(("127.0.0.1", port))
        return True
    except:
        pass
    return False

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

@arg('projectname', default='sample-project', help='project name')
def create(projectname):
    PATH_FRAMEWORK = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    PATH_PROJECT = os.path.join(os.getcwd(), projectname)

    if os.path.isdir(PATH_PROJECT):
        return print("Already exists project path '{}'".format(PATH_PROJECT))

    # install default structures
    print("create project...")
    PATH_PUBLIC_SRC = os.path.join(PATH_FRAMEWORK, 'data', 'wizbase')
    shutil.copytree(PATH_PUBLIC_SRC, PATH_PROJECT)

    # port finder
    startport = 3000
    while portchecker(startport):
        startport = startport + 1
    
    CONFIG_PATH = os.path.join(PATH_PROJECT, 'config', 'config.py')
    f = open(CONFIG_PATH, 'r')
    data = f.read()
    f.close()
    data = data.replace("__PORT__", str(startport))
    f = open(CONFIG_PATH, 'w')
    f.write(data)
    f.close()

    # install plugins
    print("install plugin... (setting)")
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-setting', os.path.join(PATH_PROJECT, 'plugin', 'core.setting'))
    print("install plugin... (branch)")
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-branch', os.path.join(PATH_PROJECT, 'plugin', 'core.branch'))
    print("install plugin... (workspace)")
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-workspace', os.path.join(PATH_PROJECT, 'plugin', 'core.workspace'))
    print("install plugin... (theme)")
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-theme', os.path.join(PATH_PROJECT, 'plugin', 'theme'))

    print("install demo branch...")
    Repo.clone_from('https://github.com/season-framework/wiz-demo', os.path.join(PATH_PROJECT, 'branch', 'master'))

    gitpath = os.path.join(PATH_PROJECT, 'branch', 'master', '.git')
    try:
        shutil.rmtree(gitpath)
    except:
        try:
            os.remove(gitpath)
        except:
            pass