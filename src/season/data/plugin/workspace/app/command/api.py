import os
import glob

def search():
    root = wiz.request.query("root", True)
    text = wiz.request.query("text", True)
    workspace = wiz.workspace("service")
    fs = workspace.fs()
    abspath = fs.abspath()
    root_dir = os.path.join(abspath, root)
    iterator = glob.iglob(f'{root_dir}/**/*{text}*', recursive=True)
    cnt = 0
    res = []
    for f in iterator:
        if '__pycache__' in f: continue
        if f.split("/")[-1].startswith("."): continue
        f = f[len(root_dir)+1:]
        res.append(f)
        cnt = cnt + 1
        if cnt >= 10: break
    wiz.response.status(200, res)

def load():
    _path = wiz.request.query("path", True)
    workspace = wiz.workspace("service")
    fs = workspace.fs()
    abspath = fs.abspath()
    fullpath = os.path.join(abspath, _path)
    _i = os.path.join(fullpath, 'app.json')
    _c = os.path.join(fullpath, 'controller.py')
    _a = os.path.join(fullpath, 'view.ts')
    _type = "file"
    data = _path
    if os.path.isfile(_i):
        if os.path.isfile(_c): _type = "route"
        elif os.path.isfile(_a): _type = "app"

    if _type == 'route' or _type == 'app':
        data = fs.read.json(os.path.join(fullpath, "app.json"))
    
    wiz.response.status(200, dict(type=_type, data=data))
