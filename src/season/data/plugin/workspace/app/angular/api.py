workspace = wiz.workspace('service')

def list(segment):    
    apps = workspace.app.list()
    wiz.response.status(200, apps)

def update(segment):
    path = wiz.request.query("path", True)
    code = wiz.request.query("code", True)
    fs = workspace.fs("src")
    fs.write(path, code)
    wiz.response.status(200)

def build(segment):
    path = wiz.request.query("path", True)
    workspace.build(path)
    wiz.response.status(200)

def data(segment):
    path = wiz.request.query("path", "")
    fs = workspace.fs("src")
    code = fs.read(path, "")
    wiz.response.status(200, code)