import os
import glob
import re

def search():
    root = wiz.request.query("root", True)
    text = wiz.request.query("text", True)
    pattern = re.compile(text, re.IGNORECASE)
    fs = wiz.project.fs()
    abspath = fs.abspath()
    root_dir = os.path.join(abspath, root)
    iterator = glob.iglob(f'{root_dir}/**/*', recursive=True)
    res = []
    target = text.split(" ")
    excludes = []
    for f in iterator:
        # exclude
        if '__pycache__' in f: continue
        if f.split("/")[-1].startswith("."): continue
        if f.endswith("/portal.json"): continue
        if f.endswith("/app.json"): continue
        _continue = False
        for ex in excludes:
            if f.startswith(ex):
                _continue = True
                break
        if _continue: continue
        ext = f.split(".")[-1]
        if ext not in ["js", "ts", "css", "scss", "md", "sql", "html", "pug", "py", "json"]:
            continue

        code = fs.read.text(f)
        result = re.search(pattern, code)
        if result is None: continue

        data = dict(root=root, filepath=f[len(root_dir)+1:], component=None, result=[])
        for i in re.finditer(pattern, code):
            start = i.start()
            end = i.end()
            data["result"].append(dict(
                fulltext=code[start-10:end+10],
                line=len(code[:start].split("\n")),
            ))

        tmpf = "/".join(f.split("/")[:-1])
        if os.path.isfile(f'{tmpf}/app.json'):
            data["component"] = tmpf[len(root_dir)+1:]

        res.append(data)
    wiz.response.status(200, res)

def load():
    _path = wiz.request.query("path", True)
    fs = wiz.project.fs()
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
