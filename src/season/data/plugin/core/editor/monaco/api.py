import os

def load():
    id = wiz.request.query("id", True)
    fs = wiz.fs(wiz.project.path("src"))
    root = fs.abspath()
    dirpath = "app"
    if id.startswith("portal."):
        tmp = id.split(".")
        portal = tmp[1]
        id = ".".join(id.split(".")[2:])
        dirpath = f"portal/{portal}/app"
    path = f'{root}/{dirpath}/{id}'
    metadata = fs.read.json(os.path.join(path, "app.json"))
    wiz.response.status(200, metadata)
