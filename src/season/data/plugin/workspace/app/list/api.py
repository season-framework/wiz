import git
import os
import zipfile
import tempfile
import time
import shutil
import datetime
import json
import season

def controllers():
    fs = wiz.workspace("service").fs("src", "controller")
    res = []
    try:
        ctrls = fs.list()
        for ctrl in ctrls:
            if fs.isfile(ctrl) and os.path.splitext(ctrl)[-1] == ".py":
                res.append(ctrl[:-3])
    except:
        pass

    wiz.response.status(200, res)

workspace = wiz.workspace("service")
working_dir = wiz.server.path.branch
fs = workspace.fs(os.path.join(working_dir))

def list():
    projects = wiz.branch.list()
    res = []
    for project in projects:
        info = fs.read.json(os.path.join(project, "wiz.project"), dict())
        info['id'] = project
        res.append(info)
    wiz.response.status(200, res)

def download(segment):
    path = segment.path
    path = fs.abspath(path)
    
    filename = os.path.splitext(os.path.basename(path))[0] + ".zip"
    zippath = os.path.join(tempfile.gettempdir(), 'wiz', datetime.datetime.now().strftime("%Y%m%d"), str(int(time.time())), filename)
    if len(zippath) < 10: 
        wiz.response.abort(404)
    try:
        shutil.remove(zippath)
    except Exception as e:
        pass
    os.makedirs(os.path.dirname(zippath))
    zipdata = zipfile.ZipFile(zippath, 'w')

    src = os.path.join(path, "src")
    config = os.path.join(path, "config")

    for folder, subfolders, files in os.walk(path):
        if folder.startswith(src) == False and folder.startswith(config) == False: 
            continue
        for file in files:
            zipdata.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), path), compress_type=zipfile.ZIP_DEFLATED)

    zipdata.close()
    wiz.response.download(zippath, as_attachment=True, filename=filename)

def ng_download(segment):
    path = segment.path
    path = fs.abspath(os.path.join(path, "build"))
    
    filename = os.path.splitext(os.path.basename(path))[0] + ".zip"
    zippath = os.path.join(tempfile.gettempdir(), 'wiz', datetime.datetime.now().strftime("%Y%m%d"), str(int(time.time())), filename)
    if len(zippath) < 10: 
        wiz.response.abort(404)
    try:
        shutil.remove(zippath)
    except Exception as e:
        pass
    os.makedirs(os.path.dirname(zippath))
    zipdata = zipfile.ZipFile(zippath, 'w')

    ignores = ["dist", "node_modules", ".vscode"]
    for folder, subfolders, files in os.walk(path):
        isignore = False
        for ign in ignores:
            if folder.startswith(os.path.join(path, ign)):
                isignore = True
        if isignore: continue
        for file in files:
            zipdata.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), path), compress_type=zipfile.ZIP_DEFLATED)

    zipdata.close()
    wiz.response.download(zippath, as_attachment=True, filename=filename)

def upload(segment):
    path = wiz.request.query("path", True)
    files = wiz.request.files()
    for i in range(len(files)):
        f = files[i]
        name = f.filename
        name = name.split("/")
        name = "/".join(name[1:])
        name = os.path.join(path, name)
        fs.write.file(name, f)

    current_branch = wiz.branch()
    wiz.branch(path)
    wp = wiz.workspace("service")
    wp.build.clean()
    wp.build()
    wiz.branch(current_branch)

    wiz.response.status(200)

def create():
    path = wiz.request.query("path", True)
    target_path = fs.abspath(os.path.join(path, "src"))
    copyfs = wiz.workspace("ide").fs(os.path.join(season.PATH_LIB, "data"))
    copyfs.copy("sample", target_path)
    current_branch = wiz.branch()
    wiz.branch(path)
    wp = wiz.workspace("service")
    wp.build.clean()
    wp.build()
    wiz.branch(current_branch)

    wiz.response.status(200)

def git():
    path = wiz.request.query("path", True)
    target_path = fs.abspath(os.path.join(path))
    try:
        git.Repo.init(target_path)
    except:
        pass

    wiz.response.status(200)

def data():
    path = wiz.request.query("path", True)
    text = fs.read(path, "")
    wiz.response.status(200, text)

def update():
    path = wiz.request.query("path", True)
    data = wiz.request.query("data", True)
    fs.write(path, data)
    wiz.response.status(200)