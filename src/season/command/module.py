import os
import json
import shutil
import urllib.request
from argh import arg, expects_obj

PATH_FRAMEWORK = os.path.dirname(os.path.dirname(__file__))
PATH_PROJECT = os.path.join(os.getcwd())
PATH_PUBLIC = os.path.join(PATH_PROJECT, 'public')
PATH_WEBSRC = os.path.join(PATH_PROJECT, 'websrc')
PATH_MODULE = os.path.join(PATH_WEBSRC, 'modules')
PATH_TMP = os.path.join(PATH_PROJECT, '.tmp')
PATH_CONFIG = os.path.join(PATH_PROJECT, 'sf.json')

# common functions
try:
    f = open(PATH_CONFIG)
    config = json.load(f)
    f.close()
except:
    config = dict()
def get_config(key, default=None):
    try:
        return config[key]
    except:
        return default

def write_file(path, content):
    f = open(path, mode="w")
    f.write(content)
    f.close()

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def clear_tmp():
    print("clear tmp directory...")
    try:
        shutil.rmtree(PATH_TMP)
    except:
        pass

def check_module(path):
    module_comp = ['controller', 'resources', 'view', 'model', 'lib']
    for comp in module_comp:
       if os.path.isdir(os.path.join(path, comp)):
           return True
    return False

def git(uri, path):
    os.system('git clone {} {}'.format(uri, path))
    if os.path.isdir(os.path.join(path, '.git')) == False:
        raise Exception('Not git repo')

# create module
def module_create(namespace):
    PATH_TARGET = os.path.join(PATH_MODULE, namespace)
    if os.path.isdir(PATH_TARGET):
        print("Module '{}' already exists".format(namespace))
        return

    PATH_SOURCE = os.path.join(PATH_PROJECT, 'websrc', 'modules', 'intro')
    PATH_SOURCE = get_config("default.module", PATH_SOURCE)

    # if source url starts with http, use git
    if PATH_SOURCE[:4] == "http":
        os.makedirs(PATH_TMP, exist_ok=True)
        PATH_GIT = os.path.join(PATH_TMP, "module")
        try:
            git(PATH_SOURCE, PATH_GIT)
        except:
            pass
        if check_module(PATH_GIT):
            try:
                shutil.rmtree(os.path.join(PATH_GIT, '.git'))
            except:
                pass
            PATH_SOURCE = PATH_GIT

    if os.path.isdir(PATH_SOURCE) == False:
        print(f"not found default module. change to framework default.")
        PATH_SOURCE = os.path.join(PATH_PROJECT, 'websrc', 'modules', 'intro')

    os.makedirs(PATH_TARGET, exist_ok=True)
    copytree(PATH_SOURCE, PATH_TARGET)

    clear_tmp()
    print(f"success copy '{namespace}' module!")

# remove module
def module_remove(namespace):
    PATH_TARGET = os.path.join(PATH_MODULE, namespace)

    if os.path.isdir(PATH_TARGET):
        res = input(f"Are you sure to delete '{namespace}' module? [yes/no] ")
        if res != 'yes' and res != 'y':
            return
    else:
        print(f"Module '{namespace}' is not exists")
        return
    
    shutil.rmtree(PATH_TARGET)
    print(f"Module '{namespace}' is deleted")

# add module
def module_add(namespace, uri):
    PATH_TARGET = os.path.join(PATH_MODULE, namespace)
    if os.path.isdir(PATH_TARGET):
        print("Module '{}' already exists".format(namespace))
        return

    is_rebuild = True
    if os.path.isdir(uri):
        if check_module(uri) == False:
            print("this folder is not structed for websrc.")
            return

        print(f"copy '{namespace}' module from... '{uri}'")
        os.makedirs(PATH_TARGET, exist_ok=True)
        copytree(uri, PATH_TARGET)
        is_rebuild = False
    
    if is_rebuild:
        print("create temp directory for git repo...")
        os.makedirs(PATH_TMP, exist_ok=True)
        PATH_GIT = os.path.join(PATH_TMP, "module")

        print("try clone from git repository...")
        try:
            git(uri, PATH_GIT)
        except:
            pass

        if check_module(PATH_GIT):
            try:
                shutil.rmtree(os.path.join(PATH_GIT, '.git'))
            except:
                pass
            print(f"copy '{namespace}' module from temporary directory...")
            os.makedirs(PATH_TARGET, exist_ok=True)
            copytree(PATH_GIT, PATH_TARGET)
            is_rebuild = False
        else:
            print("this git repository is not structed for websrc.")
    
    clear_tmp()
    if is_rebuild:
        print(f"fail to add '{namespace}' module")
        return
    print(f"success copy '{namespace}' module!")

# command api
@arg('action', default=None, help='import, remove, create')
@arg('namespace', default=None, help='module name')
@arg('--uri', help='https://github.com/season-framework/module-name')
def module(action, namespace, uri=None):
    if os.path.isdir(PATH_PUBLIC) == False or os.path.isdir(PATH_WEBSRC) == False:
        print("Invalid Project path: season framework structure not found in this folder.")
        return
    
    if action == 'add' or action == 'import':
        return module_add(namespace, uri)

    if action == 'create':
        return module_create(namespace)

    if action == 'remove' or action == 'delete' or action == 'rm':
        return module_remove(namespace)