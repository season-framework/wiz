import os
import zipfile
import tempfile
import time
import shutil
import datetime
import json
import season
from season.core.builder.base import Converter
import subprocess
import sys

python_executable = str(sys.executable)
if wiz.server.config.boot.python_executable is not None:
    python_executable = wiz.server.config.boot.python_executable

def coreupgrade():
    package = 'season'
    output = subprocess.run([python_executable, "-m", "pip", "install", str(package), "--upgrade"], capture_output=True)
    wiz.response.status(200, str(output.stdout.decode("utf-8")))
    
workspace = wiz.workspace("ide")
fs = workspace.fs("..")

def upgrade():
    plugin_id = wiz.request.query("plugin", True)
    plugin = season.plugin(wiz.server.path.root)
    try:
        plugin.upgrade(plugin_id)
    except Exception as e:
        wiz.response.status(500, str(e))
    wiz.response.status(200)

def list(segment):
    path = wiz.request.query("path", True)
    segment = path.split("/")
    res = []

    if fs.isdir(path):
        if len(segment) == 1:
            files = fs.files(path)
            for name in files:
                fpath = os.path.join(path, name)
                if fs.isdir(fpath) == False:
                    continue
                plugin = fs.read.json(os.path.join(fpath, "plugin.json"), dict())
                title = name
                if 'title' in plugin and len(plugin['title']) > 0:
                    title = plugin['title']
                res.append(dict(name=title, path=fpath, type='folder', meta=plugin))
            wiz.response.status(200, res)
            
        elif len(segment) == 2:
            res.append(dict(name='app', path=os.path.join(path, 'app'), type='mod.app'))
            res.append(dict(name='editor', path=os.path.join(path, 'editor'), type='mod.app'))
            res.append(dict(name='Plugin Info', path=os.path.join(path, 'plugin.json'), type='file', meta=dict(icon="fa-solid fa-info", editor="info")))
            res.append(dict(name='Shortcut', path=os.path.join(path, 'shortcut.ts'), type='file', meta=dict(icon="fa-solid fa-keyboard")))
            res.append(dict(name='README', path=os.path.join(path, 'README.md'), type='file', meta=dict(icon="fa-solid fa-book")))
            wiz.response.status(200, res)
        
        elif len(segment) == 3:
            mod = segment[2]
            files = fs.files(path)
            for name in files:
                fpath = os.path.join(path, name)
                if fs.isfile(os.path.join(fpath, 'app.json')):
                    appinfo = fs.read.json(os.path.join(fpath, 'app.json'))
                    res.append(dict(name=appinfo['title'], path=fpath, type='app', meta=appinfo))
            wiz.response.status(200, res)
 
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
    extension = '.wizplug' if len(path.split("/")) == 2 else '.zip'
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

    psegment = path.split("/")
    if len(psegment) > 3:
        modname = psegment[1]
        apptype = psegment[2]
        appid = psegment[3]
        appjsonpath = os.path.join("plugin", modname, apptype, appid, "app.json")
        tspath = os.path.join("plugin", modname, apptype, appid, "view.ts")

        if fs.isfile(appjsonpath):
            tscode = fs.read(tspath, "")
            appjson = fs.read.json(appjsonpath)

            app_id = f"{modname}.{apptype}.{appid}"
            converter = Converter()
            selector = converter.component_selector(app_id)
            cinfo = converter.angular_component_info(tscode)

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
    fs = workspace.fs("..", path)
    files = wiz.request.files()
    notuploaded = []
    
    for i in range(len(files)):
        f = files[i]
        name = f.filename
        app_id = ".".join(os.path.splitext(name)[:-1])
        if os.path.splitext(name)[-1] != ".wizplug":
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
    fs = workspace.fs("..", path)

    files = wiz.request.files()
    notuploaded = []
    
    for i in range(len(files)):
        f = files[i]
        name = f.filename
        app_id = ".".join(os.path.splitext(name)[:-1])
        if os.path.splitext(name)[-1] != ".wizplugapp":
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
    work = wiz.workspace("ide")
    work.build()
    wiz.response.status(200)