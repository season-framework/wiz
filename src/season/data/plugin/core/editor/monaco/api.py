import os
from glob import glob

def load():
    id = wiz.request.query("id", True)
    fs = wiz.fs()
    abspath = fs.abspath()
    root = "src"
    if id.startswith("portal."):
        tmp = id.split(".")
        portal = tmp[1]
        id = ".".join(id.split(".")[2:])
        root = f"portal/{portal}"
    res = glob(f'{abspath}/{root}/*/{id}', recursive=True)
    if len(res) == 0:
        wiz.response.status(404)
    path = res[0]
    metadata = fs.read.json(os.path.join(path, "app.json"))
    wiz.response.status(200, metadata)
