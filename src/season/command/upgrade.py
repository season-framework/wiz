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

def upgrade():
    PATH_FRAMEWORK = os.path.dirname(os.path.dirname(__file__))
    
    # check wiz structure
    publicpath = os.path.join(season.path.project, 'public')
    apppath = os.path.join(publicpath, 'app.py')
    if os.path.isfile(apppath) == False:
        print("Invalid Project path: wiz structure not found in this folder.")
        return

    fs = season.util.os.FileSystem(season.path.project)

    # remove old versions
    fs.remove("cache")
    fs.remove("config")
    fs.remove("merge")
    fs.remove("plugin")
    fs.remove("public")
    fs.remove("wiz.json")

    # install default structure
    print("init wiz structure...")
    PATH_PUBLIC_SRC = os.path.join(PATH_FRAMEWORK, 'data')
    fs.copy(os.path.join(PATH_PUBLIC_SRC, 'config'), fs.abspath('config'))
    fs.copy(os.path.join(PATH_PUBLIC_SRC, 'public'), fs.abspath('public'))
    fs.copy(os.path.join(PATH_PUBLIC_SRC, 'wiz.json'), fs.abspath('wiz.json'))

    # config
    print("search run port ...")
    startport = 3000
    while portchecker(startport):
        startport = startport + 1

    data = fs.read(os.path.join('config', 'server.py'))
    data = data.replace("__PORT__", str(startport))
    fs.write(os.path.join('config', 'server.py'), data)
    fs.write(os.path.join('config', 'installed.py'), "started = '" + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S') + "'")
    print(f"set initial port as {startport}")

    print("install ide...")
    fs = season.util.os.FileSystem(season.path.project)
    ide="https://github.com/season-framework/wiz-ide"
    git.Repo.clone_from(ide, fs.abspath("plugin"))

    # app namespace remove
    branches = fs.use("branch").files()
    for branch in branches:
        print(f"[wiz] migrate `apps` in `{branch}` branch")
        appfs = fs.use(os.path.join("branch", branch, "apps"))
        apps = appfs.files()
        for app_id in apps:
            app = appfs.use(app_id).read.json("app.json")
            if 'namespace' in app:
                app['id'] = app['namespace']
                del app['namespace']
                appfs.use(app_id).write.json("app.json", app)

            if app_id != app['id']:
                appfs.rename(app_id, app['id'])
                newid = app['id']
                print(f"  - `{newid}`")

        print(f"[wiz] migrate `routes` in `{branch}` branch")
        appfs = fs.use(os.path.join("branch", branch, "routes"))
        apps = appfs.files()
        for app_id in apps:
            app = appfs.use(app_id).read.json("app.json")
            if 'namespace' in app:
                app['id'] = season.util.string.translate_id(app['route'])
                del app['namespace']
                appfs.use(app_id).write.json("app.json", app)

            if app_id != app['id']:
                appfs.rename(app_id, app['id'])
                newid = app['id']
                print(f"  - `{newid}`")

    print("init local remote git...")
    fs = season.util.os.FileSystem(os.path.join(season.path.project, 'branch'))
    srcfs = season.util.os.FileSystem(os.path.join(season.path.project, 'origin'))
    srcfs.delete()
    git.Repo.init(srcfs.abspath(), bare=True)
    for branch in branches:
        repo = git.Repo.init(fs.abspath(branch))
        try:
            origin = repo.remote(name='wiz')
            repo.delete_remote(origin)
        except:
            pass
        origin = repo.create_remote('wiz', srcfs.abspath())
        origin.push(branch)
