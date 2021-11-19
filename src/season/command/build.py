import os
import shutil
from argh import arg, expects_obj
import time

PATH_FRAMEWORK = os.path.dirname(os.path.dirname(__file__))
PATH_PROJECT = os.path.join(os.getcwd())
PATH_PUBLIC = os.path.join(PATH_PROJECT, 'public')
PATH_WEBSRC = os.path.join(PATH_PROJECT, 'websrc')
PATH_TMP = os.path.join(PATH_PROJECT, '.tmp')

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def clear_websrc():
    print("clear exist websrc...")
    try:
        shutil.rmtree(PATH_WEBSRC)
    except:
        pass

def clear_tmp():
    print("clear tmp directory...")
    try:
        shutil.rmtree(PATH_TMP)
    except:
        pass

def check_websrc(path):
    if os.path.isdir(os.path.join(path, "app")) == False or os.path.isdir(os.path.join(path, "modules")) == False:
        return False
    return True

def git(uri, path):
    os.system('git clone {} {}'.format(uri, path))
    if os.path.isdir(os.path.join(path, '.git')) == False:
        raise Exception('Not git repo')

@arg('--uri', default=None, help='https://github.com/season-framework/something | /home/user/myproject/websrc')
def build(uri=None):
    if os.path.isdir(PATH_PUBLIC) == False:
        print("invalid project path: season framework structure not found in this folder.")
        return

    is_rebuild = False

    if uri is not None:
        if os.path.isdir(PATH_WEBSRC):
            res = input("already exists websrc folder. replace to another websrc? [yes/no] ")
            if res == 'yes' or res == 'y':
                is_rebuild = True
        else:
            is_rebuild = True

    timeinterval = round(time.time()*1000)

    # import from websrc source
    if is_rebuild:
        is_rebuild = True
        
        # build from local folder
        if os.path.isdir(uri):
            if check_websrc(uri) == False:
                print("this folder is not structed for websrc.")
                return

            clear_websrc()
            print(f"copy from... '{uri}'")
            os.makedirs(PATH_WEBSRC, exist_ok=True)
            copytree(uri, PATH_WEBSRC)
            is_rebuild = False
            print(f"success copy websrc!")
        
        if is_rebuild:
            print("create temp directory for git repo...")
            os.makedirs(PATH_TMP, exist_ok=True)
            PATH_GIT = os.path.join(PATH_TMP, "websrc")

            print("try clone from git repository...")
            try:
                git(uri, PATH_GIT)
            except:
                pass

            if check_websrc(PATH_GIT):
                clear_websrc()
                print(f"copy...")
                os.makedirs(PATH_WEBSRC, exist_ok=True)
                copytree(PATH_GIT, PATH_WEBSRC)
                is_rebuild = False
                print(f"success copy websrc!")
            else:
                print("this git repository is not structed for websrc.")

    # build
    # TODO: add build process using websrc build folder

    # finish task
    clear_tmp()
    timeinterval = round(time.time()*1000) - timeinterval
    timeinterval = round(timeinterval / 1000)
    print(f"finish to build in {timeinterval}s. run season framework using `sf run`")
