import os
import zipfile
workspace = wiz.workspace('service')

def list(segment):
    mode = wiz.request.query("mode", True)
    apps = workspace.app.list()
    res = []
    for app in apps:
        if app['mode'] == mode:
            res.append(app)
    wiz.response.status(200, res)

def exists(segment):
    path = wiz.request.query("id", True)
    fs = workspace.fs(os.path.join("src", "app"))
    wiz.response.status(200, fs.exists(path))

def update(segment):
    path = wiz.request.query("path", True)
    code = wiz.request.query("code", True)
    fs = workspace.fs("src")
    fs.write(path, code)
    wiz.server.socket.bind()
    wiz.response.status(200)

def build(segment):
    path = wiz.request.query("path", True)
    entire = wiz.request.query("entire", False)
    if entire: workspace.build()
    else: workspace.build(path)
    wiz.response.status(200)

def data(segment):
    path = wiz.request.query("path", "")
    fs = workspace.fs("src")
    code = fs.read(path, "")
    wiz.response.status(200, code)

def move(segment):
    _from = wiz.request.query("from", True)
    _to = wiz.request.query("to", True)
    fs = workspace.fs(os.path.join("src", "app"))
    if fs.exists(_to):
        wiz.response.status(400)
    if fs.exists(_from) == False:
        wiz.response.status(400)
    fs.move(_from, _to)
    wiz.response.status(200)

def remove(segment):
    path = wiz.request.query("path", True)
    fs = workspace.fs("src")
    if len(path.split("/")) > 1 and path.split("/")[0] == "app":
        fs.delete(path)
    wiz.response.status(200)

def upload(segment):
    files = wiz.request.files()
    notuploaded = []
    for i in range(len(files)):
        f = files[i]
        name = f.filename
        app_id = ".".join(os.path.splitext(name)[:-1])
        if os.path.splitext(name)[-1] != ".wizapp":
            notuploaded.append(app_id)
            continue

        fs = workspace.fs("src", "app")
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
        appinfo['namespace'] = ".".join(app_id.split(".")[1:])
        appinfo['mode'] = app_id.split(".")[0]
        fs.write.json(os.path.join(app_id, "app.json"), appinfo)

    wiz.response.status(200, notuploaded)