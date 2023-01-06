import os
import zipfile
import tempfile
import time
import shutil
import datetime
import json

workspace = wiz.workspace("service")
fs = workspace.fs()

def layout():
    mode = "layout"
    apps = workspace.app.list()
    res = []
    for app in apps:
        if app['mode'] == mode:
            res.append(app)
    wiz.response.status(200, res)

def controller():
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

def list(segment):
    path = wiz.request.query("path", True)
    segment = path.split("/")
    res = []

    if len(segment) == 1 and segment[0] == "src":
        res.append(dict(name='angular', path=os.path.join(path, 'angular'), type='angular'))
        res.append(dict(name='apps/page', path=os.path.join(path, 'app', 'page'), type='mod.page'))
        res.append(dict(name='apps/component', path=os.path.join(path, 'app', 'component'), type='mod.component'))
        res.append(dict(name='apps/layout', path=os.path.join(path, 'app', 'layout'), type='mod.layout'))
        res.append(dict(name='api', path=os.path.join(path, 'route'), type='mod.route'))
        res.append(dict(name='libs', path=os.path.join(path, 'angular', 'libs'), type='mod.libs'))
        res.append(dict(name='styles', path=os.path.join(path, 'angular', 'styles'), type='mod.styles'))
        res.append(dict(name='assets', path=os.path.join(path, 'assets'), type='mod.folder'))
        res.append(dict(name='controller', path=os.path.join(path, 'controller'), type='mod.folder'))
        res.append(dict(name='model', path=os.path.join(path, 'model'), type='mod.folder'))
        res.append(dict(name='config', path=os.path.join('config'), type='mod.folder'))
        wiz.response.status(200, res)
    
    if len(segment) == 3 and segment[1] == 'app':
        mode = segment[2]
        path = "/".join(segment[:2])
        files = fs.files(path)
        for name in files:
            fpath = os.path.join(path, name)
            if fs.isfile(os.path.join(fpath, 'app.json')):
                appinfo = fs.read.json(os.path.join(fpath, 'app.json'))
                if appinfo['mode'] == mode:
                    res.append(dict(name=appinfo['title'], path=fpath, type='app', meta=appinfo))
        wiz.response.status(200, res)
    
    if len(segment) == 2 and segment[1] == 'route':
        files = fs.files(path)
        for name in files:
            fpath = os.path.join(path, name)
            if fs.isfile(os.path.join(fpath, 'app.json')):
                appinfo = fs.read.json(os.path.join(fpath, 'app.json'))
                res.append(dict(name=appinfo['route'], path=fpath, type='route', meta=appinfo))
        wiz.response.status(200, res)
    
    if fs.isdir(path): 
        files = fs.files(path)
        for name in files:
            fpath = os.path.join(path, name)
            ftype = 'file' if fs.isfile(fpath) else 'folder'
            res.append(dict(name=name, path=fpath, type=ftype))
        
        wiz.response.status(200, res)

    wiz.response.status(404, [])

def exists(segment):
    path = wiz.request.query("path", True)
    wiz.response.status(200, fs.exists(path))

def create():
    path = wiz.request.query("path", True)
    _type = wiz.request.query("type", True)

    if fs.exists(path):
        wiz.response.status(401, False)
    
    try:
        if _type == 'folder':
            fs.makedirs(path)
        else:
            fs.write(path, "")
    except:
        wiz.response.status(500, False)

    wiz.response.status(200, True)

def delete():
    path = wiz.request.query("path", True)
    if len(path) == 0:
        wiz.response.status(401, False)
    if fs.exists(path):
        fs.delete(path)
    wiz.response.status(200, True)

def move():
    path = wiz.request.query("path", True)
    to = wiz.request.query("to", True)
    if len(path) == 0 or len(to) == 0:
        wiz.response.status(401, False)
    if fs.exists(path) == False:
        wiz.response.status(401, False)
    if fs.exists(to):
        wiz.response.status(401, False)
    fs.move(path, to)
    wiz.response.status(200, True)

def read():
    path = wiz.request.query("path", True)
    if fs.isfile(path):
        wiz.response.status(200, fs.read(path, ""))
    wiz.response.status(404)

def download(segment):
    path = segment.path
    extension = '.wizportal' if len(path.split("/")) == 2 else '.zip'
    path = fs.abspath(path)

    if fs.isdir(path):
        filename = os.path.splitext(os.path.basename(path))[0] + extension
        zippath = os.path.join(tempfile.gettempdir(), 'wiz', datetime.datetime.now().strftime("%Y%m%d"), str(int(time.time())), filename)
        if len(zippath) < 10: 
            wiz.response.abort(404)
        try:
            shutil.remove(zippath)
        except Exception as e:
            pass
        os.makedirs(os.path.dirname(zippath))
        zipdata = zipfile.ZipFile(zippath, 'w')
        for folder, subfolders, files in os.walk(path):
            for file in files:
                zipdata.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), path), compress_type=zipfile.ZIP_DEFLATED)
        zipdata.close()
        wiz.response.download(zippath, as_attachment=True, filename=filename)
    else:
        wiz.response.download(path, as_attachment=True)

    wiz.response.status(200, segment)

def update(segment):
    path = wiz.request.query("path", True)
    code = wiz.request.query("code", True)
    fs.write(path, code)
    wiz.response.status(200)

def upload(segment):
    path = wiz.request.query("path", True)
    filepath = wiz.request.query("filepath", "[]")
    filepath = json.loads(filepath)
    files = wiz.request.files()
    for i in range(len(files)):
        f = files[i]
        if len(filepath) > 0: name = filepath[i]
        else: name = f.filename
        name = os.path.join(path, name)
        fs.write.file(name, f)
    wiz.response.status(200)

def upload_root(segment):
    path = wiz.request.query("path", True)
    fs = workspace.fs(path)
    files = wiz.request.files()
    notuploaded = []
    
    for i in range(len(files)):
        f = files[i]
        name = f.filename
        app_id = ".".join(os.path.splitext(name)[:-1])
        if os.path.splitext(name)[-1] != ".wizportal":
            notuploaded.append(app_id)
            continue

        if fs.exists(app_id):
            notuploaded.append(app_id)
            continue

        fs.write.file(name, f)

        zippath = fs.abspath(name)
        unzippath = fs.abspath(app_id)
        with zipfile.ZipFile(zippath, 'r') as zip_ref:
           zip_ref.extractall(unzippath)

        fs.delete(name)

    wiz.response.status(200, notuploaded)

def upload_app(segment):
    path = wiz.request.query("path", True)
    path = "/".join(path.split("/")[:-1])
    fs = workspace.fs(path)

    files = wiz.request.files()
    notuploaded = []
    
    for i in range(len(files)):
        f = files[i]
        name = f.filename
        app_id = ".".join(os.path.splitext(name)[:-1])
        if os.path.splitext(name)[-1] != ".wizapp":
            notuploaded.append(app_id)
            continue

        if fs.exists(app_id):
            notuploaded.append(app_id)
            continue

        fs.write.file(name, f)

        zippath = fs.abspath(name)
        unzippath = fs.abspath(app_id)
        with zipfile.ZipFile(zippath, 'r') as zip_ref:
           zip_ref.extractall(unzippath)

        fs.delete(name)

        appinfo = fs.read.json(os.path.join(app_id, "app.json"), dict())
        appinfo['id'] = app_id
        appinfo['namespace'] = app_id
        fs.write.json(os.path.join(app_id, "app.json"), appinfo)

    wiz.response.status(200, notuploaded)

def build(segment):
    workspace.build()
    workspace.route.build()
    wiz.response.status(200)
