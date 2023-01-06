import os
from glob import glob

def load():
    id = wiz.request.query("id", True)
    workspace = wiz.workspace("service")
    fs = workspace.fs()
    abspath = fs.abspath()
    res = glob(f'{abspath}/src/*/{id}', recursive=True)
    if len(res) == 0:
        wiz.response.status(404)
    path = res[0]
    metadata = fs.read.json(os.path.join(path, "app.json"))
    wiz.response.status(200, metadata)
