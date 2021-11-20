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
    PATH_FRAMEWORK = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    PATH_PROJECT = os.path.join(os.getcwd(), projectname)

    if os.path.isdir(PATH_PROJECT):
        return print("Already exists project path '{}'".format(PATH_PROJECT))

    PATH_PUBLIC_SRC = os.path.join(PATH_FRAMEWORK, 'data', 'wizbase')

    shutil.copytree(PATH_PUBLIC_SRC, PATH_PROJECT)
    