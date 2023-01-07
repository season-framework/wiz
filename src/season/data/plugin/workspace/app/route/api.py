import os
workspace = wiz.workspace('service')

def list(segment):
    routes = workspace.route.list()
    wiz.response.status(200, routes)

def exists(segment):
    path = wiz.request.query("id", True)
    fs = workspace.fs(os.path.join("src", "route"))
    wiz.response.status(200, fs.exists(path))

def update(segment):
    path = wiz.request.query("path", True)
    code = wiz.request.query("code", True)
    fs = workspace.fs("src")
    fs.write(path, code)
    try:
        workspace.route.build()
    except:
        pass
    wiz.response.status(200)

def data(segment):
    path = wiz.request.query("path", "")
    fs = workspace.fs("src")
    code = fs.read(path, "")
    wiz.response.status(200, code)

def move(segment):
    _from = wiz.request.query("from", True)
    _to = wiz.request.query("to", True)
    fs = workspace.fs(os.path.join("src", "route"))
    if fs.exists(_to):
        wiz.response.status(400)
    if fs.exists(_from) == False:
        wiz.response.status(400)
    fs.move(_from, _to)
    wiz.response.status(200)

def remove(segment):
    path = wiz.request.query("path", True)
    fs = workspace.fs("src")
    if len(path.split("/")) > 1 and path.split("/")[0] == "route":
        fs.delete(path)
    workspace.route.build()
    wiz.response.status(200)