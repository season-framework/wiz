import git as Git
import os
import zipfile
import tempfile
import time
import shutil
import datetime
import json

working_dir = wiz.server.path.project
fs = wiz.project.fs(os.path.join(working_dir))

def download(segment):
    path = segment.path
    path = fs.abspath(path)
    filename = os.path.splitext(os.path.basename(path))[0] + ".wizproject"
    zippath = os.path.join(tempfile.gettempdir(), 'wiz', datetime.datetime.now().strftime("%Y%m%d"), str(int(time.time())), filename)
    if len(zippath) < 10: 
        wiz.response.abort(404)
    try:
        shutil.remove(zippath)
    except Exception as e:
        pass
    os.makedirs(os.path.dirname(zippath))
    zipdata = zipfile.ZipFile(zippath, 'w')

    contains = ["src", "portal", "config", ".git"]

    for folder, subfolders, files in os.walk(path):
        check = False
        for contain in contains:
            if folder.startswith(os.path.join(path, contain)):
                check = True
        if folder == path:
            check = True
        if check == False: 
            continue

        for file in files:
            zipdata.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), path), compress_type=zipfile.ZIP_DEFLATED)

    zipdata.close()
    wiz.response.download(zippath, as_attachment=True, filename=filename)

def git():
    path = wiz.request.query("path", True)
    target_path = fs.abspath(os.path.join(path))
    repo = Git.Repo.init(target_path)
    
    resp = dict()

    author = dict()
    try: author['name'] = repo.config_reader().get_value("user", "name")
    except: author['name'] = 'wiz'
    try: author['email'] = repo.config_reader().get_value("user", "email")
    except: author['email'] = 'wiz@localhost'
    resp['author'] = author
    resp['remote'] = [x.name for x in repo.remotes]
    
    wiz.response.status(200, resp)

def git_update():
    path = wiz.request.query("path", True)
    name = wiz.request.query("name", None)
    email = wiz.request.query("email", None)

    target_path = fs.abspath(os.path.join(path))
    repo = Git.Repo.init(target_path)

    if name is not None:
        repo.config_writer().set_value("user", "name", name).release()
    if email is not None:
        repo.config_writer().set_value("user", "email", email).release()

    wiz.response.status(200)

def rebuild():
    path = wiz.request.query("path", True)
    current = wiz.project()
    wiz.project(path)
    builder = wiz.ide.plugin.model("builder")
    builder.clean()
    builder.build()
    wiz.project(current)
    wiz.response.status(200)

def delete():
    path = wiz.request.query("path", True)
    fs.delete(path)
    wiz.response.status(200)