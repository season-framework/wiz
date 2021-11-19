import os
import shutil
from argh import arg, expects_obj

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
    PATH_FRAMEWORK = os.path.dirname(os.path.dirname(__file__))
    PATH_PROJECT = os.path.join(os.getcwd(), projectname)
    PATH_PUBLIC = os.path.join(PATH_PROJECT, 'public')
    PATH_WEBSRC = os.path.join(PATH_PROJECT, 'websrc')

    if os.path.isdir(PATH_PROJECT):
        return print("Already exists project path '{}'".format(PATH_PROJECT))

    PATH_PUBLIC_SRC = os.path.join(PATH_FRAMEWORK, 'data', 'public')
    PATH_WEBSRC_SRC = os.path.join(PATH_FRAMEWORK, 'data', 'websrc')

    os.makedirs(PATH_PROJECT, exist_ok=True)
    os.makedirs(PATH_PUBLIC, exist_ok=True)
    copytree(PATH_PUBLIC_SRC, PATH_PUBLIC)
    os.makedirs(PATH_WEBSRC, exist_ok=True)
    copytree(PATH_WEBSRC_SRC, PATH_WEBSRC)
    