import os
import math
import json
import time
import datetime
import shutil
import zipfile
import tempfile
import season
import git

builder = wiz.ide.plugin.model("builder")
Namespace = wiz.ide.plugin.model("src/build/namespace")
Annotator = wiz.ide.plugin.model("src/build/annotator")
fs = wiz.project.fs("src")

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
    
    cachefs = season.util.fs(fs.abspath(".cache"))
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

def tree():
    path = wiz.request.query("path", True)

    children = []

    def addChild(topath, title, _path=None, _type=None, _meta=None):
        _item = dict(title=title, id=os.path.join(path, title), type='folder', root_id=topath)
        if _path is not None: _item['id'] = _path
        if _type is not None: _item['type'] = _type
        if _meta is not None: _item['meta'] = _meta
        children.append(_item)

    def driveItem(path, root=None):
        item = dict()
        item['id'] = path
        item['type'] = 'folder' if fs.isdir(path) else 'file'
        item['title'] = os.path.basename(path)
        if len(path.split('/')) == 2:
            plugin = fs.read.json(os.path.join(path, "portal.json"), dict())
            if 'title' in plugin and len(plugin['title']) > 0: item['title'] = plugin['title']
            item['meta'] = plugin
        if root is None: item['root_id'] = os.path.dirname(path)
        else: item['root_id'] = root
        return item

    if path == '' or path == 'portal':
        path = 'portal'
        root = dict(id='portal', title='portal', type='folder')

        files = fs.files(path)
        for name in files:
            fpath = os.path.join(path, name)
            if fs.isdir(fpath) == False:
                continue
            plugin = fs.read.json(os.path.join(fpath, "portal.json"), dict())
            title = name
            if 'title' in plugin and len(plugin['title']) > 0:
                title = plugin['title']
            
            addChild('portal', title, _path=fpath, _type='folder', _meta=plugin)
        
        wiz.response.status(200, dict(root=root, children=children))
    
    segment = path.split("/")

    if len(segment) == 3 and segment[2] == 'sample':
        if fs.isdir(path) == False: fs.makedirs(path)
        root = driveItem(path)

        addChild(path, 'page')
        addChild(path, 'component')
        addChild(path, 'layout')
        
        wiz.response.status(200, root=root, children=children)

    if len(segment) > 3 and segment[2] == 'sample':
        mod = segment[3]
        if mod in ['layout', 'component', 'page']:
            spath = os.path.join(*segment[:3])
            root = driveItem(spath)
            root['id'] = path
            root['title'] = mod
            files = fs.files(spath)

            for name in files:
                if name.split(".")[0] != mod:
                    continue
                fpath = os.path.join(spath, name)
                if fs.isfile(os.path.join(fpath, 'app.json')):
                    appinfo = fs.read.json(os.path.join(fpath, 'app.json'))
                    addChild(path, appinfo['title'], _path=fpath, _type=mod, _meta=appinfo)

            wiz.response.status(200, root=root, children=children)

    if fs.isdir(path) == False:
        wiz.response.status(404)

    if len(segment) == 2:
        plugin = fs.read.json(os.path.join(path, "portal.json"), dict())
        
        def checker(name):
            if f"use_{name}" in plugin:
                return plugin[f"use_{name}"]
            return False

        root = driveItem(path)
        
        addChild(path, 'Module Info', _path=os.path.join(path, 'portal.json'), _type='file', _meta=dict(editor='info'))
        structures = ['sample', 'app', 'widget', 'route', 'libs', 'styles', 'assets', 'controller', 'model']
        for st in structures:
            if checker(st): addChild(path, st)
        addChild(path, 'README', _path=os.path.join(path, 'README.md'), _type='file')
        
        wiz.response.status(200, root=root, children=children)

    if len(segment) == 3 and segment[2] in ['app', 'route', 'widget']:
        mod = segment[2]
        root = driveItem(path)

        files = fs.files(path)
        for name in files:
            fpath = os.path.join(path, name)
            if fs.isfile(os.path.join(fpath, 'app.json')):
                appinfo = fs.read.json(os.path.join(fpath, 'app.json'))
                if mod == 'route':
                    addChild(path, appinfo['route'], _path=fpath, _type='route', _meta=appinfo)
                else:
                    appinfo['type'] = mod
                    addChild(path, appinfo['title'], _path=fpath, _type='app', _meta=appinfo)

        wiz.response.status(200, root=root, children=children)

    root = driveItem(path)
    files = fs.files(path)
    for name in files:
        fpath = os.path.join(path, name)
        ftype = 'file' if fs.isfile(fpath) else 'folder'
        addChild(path, name, _path=fpath, _type=ftype)
              
    wiz.response.status(200, root=root, children=children)

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

    extension = ".zip"
    if len(path.split("/")) == 2:
        extension = ".wizportal"
    if fs.exists(os.path.join(path, "app.json")):
        extension = ".wizapp"

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
    fs.write(path, code)

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
            cinfo = Annotator.definition.ngComponentDesc(tscode)
            injector = [f'[{x}]=""' for x in cinfo['inputs']] + [f'({x})=""' for x in cinfo['outputs']]
            injector = ", ".join(injector)
            appjson['template'] = selector + "(" + injector + ")"
            fs.write.json(appjsonpath, appjson)

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
    fs = wiz.project.fs("src", path)
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
    fs = wiz.project.fs("src", path)

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
