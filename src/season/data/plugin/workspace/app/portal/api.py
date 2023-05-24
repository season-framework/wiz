import os
import zipfile
import tempfile
import time
import shutil
import datetime
import json
import season
import git

builder = wiz.model("workspace/builder")
Namespace = wiz.model("workspace/build/namespace")
Definition = wiz.model("workspace/build/annotation/definition")
workspace = wiz.workspace("service")
fs = workspace.fs()

def install_sample():
    path = wiz.request.query("path", True)
    name = path.split("/")[-1]
    mode = name.split(".")[0]
    if fs.exists(os.path.join("src", "app", name)):
        wiz.response.status(404)
    
    fs.copy(path, os.path.join("src", "app", name))
    try:
        appinfo = fs.read.json(os.path.join("src", "app", name, "app.json"))
        appinfo['mode'] = mode
        appinfo['namespace'] = appinfo['namespace'][len(mode)+1:]
        fs.write.json(os.path.join("src", "app", name, "app.json"), appinfo)
    except:
        pass

    wiz.response.status(200)

def upgrade():
    path = wiz.request.query("path", True)
    info = fs.read.json(os.path.join(path, "portal.json"), dict())
    if 'repo' not in info:
        wiz.response.status(404, True)
    
    cachefs = season.util.os.FileSystem(fs.abspath(".cache"))
    cachefs.remove()
    
    try:
        repo = info['repo']
        downloaded = cachefs.abspath("portal")
        git.Repo.clone_from(repo, downloaded)
    except:
        pass
    
    if cachefs.exists("portal") == False:
        wiz.response.status(404, True)

    fs.remove(path)
    fs.move(cachefs.abspath("portal"), path)
    cachefs.remove()

    build()
    wiz.response.status(200, True)

def list(segment):
    path = wiz.request.query("path", True)
    segment = path.split("/")
    res = []

    if len(segment) == 1:
        files = fs.files(path)
        for name in files:
            fpath = os.path.join(path, name)
            if fs.isdir(fpath) == False:
                continue
            plugin = fs.read.json(os.path.join(fpath, "portal.json"), dict())
            title = name
            if 'title' in plugin and len(plugin['title']) > 0:
                title = plugin['title']
            res.append(dict(name=title, path=fpath, type='folder', meta=plugin))
        
        res = sorted(res, key=lambda k: k['name'])
        wiz.response.status(200, res)

    elif len(segment) == 2:
        plugin = fs.read.json(os.path.join(path, "portal.json"), dict())
        def checker(name):
            if f"use_{name}" in plugin:
                return plugin[f"use_{name}"]
            return False
        
        if checker('sample'): res.append(dict(name='sample', path=os.path.join(path, 'sample'), type='mod.sample'))
        if checker('app'): res.append(dict(name='app', path=os.path.join(path, 'app'), type='mod.app', meta=dict(icon="fa-solid fa-layer-group")))
        if checker('widget'): res.append(dict(name='widget', path=os.path.join(path, 'widget'), type='mod.app', meta=dict(icon="fa-solid fa-layer-group")))
        if checker('route'): res.append(dict(name='api', path=os.path.join(path, 'route'), type='mod.route', meta=dict(icon="fa-solid fa-link")))
        if checker('libs'): res.append(dict(name='libs', path=os.path.join(path, 'libs'), type='mod.libs', meta=dict(icon="fa-solid fa-book")))
        if checker('styles'): res.append(dict(name='styles', path=os.path.join(path, 'styles'), type='mod.styles', meta=dict(icon="fa-brands fa-css")))
        if checker('assets'): res.append(dict(name='assets', path=os.path.join(path, 'assets'), type='mod.assets', meta=dict(icon="fa-solid fa-images")))
        if checker('controller'): res.append(dict(name='controller', path=os.path.join(path, 'controller'), type='mod.controller'))
        if checker('model'): res.append(dict(name='model', path=os.path.join(path, 'model'), type='mod.model'))
        res.append(dict(name='Package Info', path=os.path.join(path, 'portal.json'), type='file', meta=dict(icon="fa-solid fa-info", editor="info")))
        res.append(dict(name='README', path=os.path.join(path, 'README.md'), type='file'))
        wiz.response.status(200, res)
    
    elif len(segment) == 3:
        mod = segment[2]
        if mod == 'sample':
            res.append(dict(name='page', path=os.path.join(path, 'page'), type='mod.sample.page'))
            res.append(dict(name='component', path=os.path.join(path, 'component'), type='mod.sample.app'))
            res.append(dict(name='layout', path=os.path.join(path, 'layout'), type='mod.sample.app'))
            wiz.response.status(200, res)
        
        if mod in ['app', 'route', 'widget']:
            files = fs.files(path)
            for name in files:
                fpath = os.path.join(path, name)
                if fs.isfile(os.path.join(fpath, 'app.json')):
                    appinfo = fs.read.json(os.path.join(fpath, 'app.json'))
                    if mod == 'route':
                        res.append(dict(name=appinfo['route'], path=fpath, type=mod, meta=appinfo))
                    else:
                        appinfo['type'] = mod
                        res.append(dict(name=appinfo['title'], path=fpath, type=mod, meta=appinfo))

            wiz.response.status(200, res)

    elif len(segment) > 3:
        mod = segment[2]
        if mod in ['app', 'widget', 'route']:
            wiz.response.status(200, res)
        
        if mod == 'sample':
            mod = segment[3]
            if mod == 'layout' or mod == 'component' or mod == 'page':
                spath = os.path.join(*segment[:3])
                files = fs.files(spath)
                for name in files:
                    if name.split(".")[0] != mod:
                        continue
                    fpath = os.path.join(spath, name)
                    if fs.isfile(os.path.join(fpath, 'app.json')):
                        appinfo = fs.read.json(os.path.join(fpath, 'app.json'))
                        res.append(dict(name=appinfo['title'], path=fpath, type=mod, meta=appinfo))

                wiz.response.status(200, res)

    files = fs.files(path)
    for name in files:
        fpath = os.path.join(path, name)
        ftype = 'file' if fs.isfile(fpath) else 'folder'
        res.append(dict(name=name, path=fpath, type=ftype))
    
    wiz.response.status(200, res)

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
    code = wiz.request.query("code", "")

    psegment = path.split("/")
    if len(psegment) > 3 and psegment[2] in ['app', 'widget']:
        modname = psegment[1]
        appid = psegment[3]

        appjsonpath = os.path.join("portal", modname, "app", appid, "app.json")
        tspath = os.path.join("portal", modname, "app", appid, "view.ts")

        if fs.isfile(appjsonpath):
            tscode = fs.read(tspath, "")
            appjson = fs.read.json(appjsonpath)
            appjson['id'] = appid
            appjson['type'] = psegment[2]

            app_id = f"portal.{modname}.{appid}"
            selector = Namespace.selector(app_id)
            cinfo = Definition.ngComponentDesc(tscode)

            injector = [f'[{x}]=""' for x in cinfo['inputs']] + [f'({x})=""' for x in cinfo['outputs']]
            injector = ", ".join(injector)
            appjson['template'] = selector + "(" + injector + ")"

            fs.write.json(appjsonpath, appjson)

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

def build():
    builder.build()
    wiz.response.status(200)

def controllers():
    module = wiz.request.query("module", None)
    res = []
    try:
        if module is not None:
            ctrls = fs.list(os.path.join("portal", module, "controller"))
            for ctrl in ctrls:
                if fs.isfile(os.path.join("portal", module, "controller", ctrl)) and os.path.splitext(ctrl)[-1] == ".py":
                    res.append(ctrl[:-3])
    except:
        pass
    wiz.response.status(200, res)
