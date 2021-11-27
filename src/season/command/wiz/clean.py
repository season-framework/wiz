import os
import shutil
from argh import arg, expects_obj
from git import Repo

def clean():
    PATH_FRAMEWORK = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    PATH_PROJECT = os.getcwd()

    print("delete cache...")
    cachepath = os.path.join(PATH_PROJECT, "cache")
    try:
        shutil.rmtree(cachepath)
    except:
        try:
            os.remove(cachepath)
        except:
            pass

    # delete plugin
    print("delete plugins...")
    pluginpath = os.path.join(PATH_PROJECT, "plugin")
    try:
        shutil.rmtree(pluginpath)
    except:
        try:
            os.remove(pluginpath)
        except:
            pass

    # install plugins
    print("install plugin... (setting)")
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-setting', os.path.join(PATH_PROJECT, 'plugin', 'core.setting'))
    print("install plugin... (branch)")
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-branch', os.path.join(PATH_PROJECT, 'plugin', 'core.branch'))
    print("install plugin... (workspace)")
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-workspace', os.path.join(PATH_PROJECT, 'plugin', 'core.workspace'))
    print("install plugin... (theme)")
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-theme', os.path.join(PATH_PROJECT, 'plugin', 'theme'))