import subprocess
import sys

builder = wiz.ide.plugin.model("builder")

def install():
    package = wiz.request.query("package", True)
    fs = builder.fs("build")
    cmd = f"cd {fs.abspath()} && npm install --save {package}"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    res = ""
    if out is not None and len(out) > 0: res = res + out.decode('utf-8').strip()
    if err is not None and len(err) > 0: res = res + "\n" + err.decode('utf-8').strip()
    builder.build()

    fs = builder.fs()
    fs.copy("build/package.json", "src/angular/package.json")

    wiz.response.status(200, res)

def uninstall():
    package = wiz.request.query("package", True)
    fs = builder.fs("build")
    cmd = f"cd {fs.abspath()} && npm uninstall --save {package}"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    res = ""
    if out is not None and len(out) > 0: res = res + out.decode('utf-8').strip()
    if err is not None and len(err) > 0: res = res + "\n" + err.decode('utf-8').strip()
    builder.build()

    fs = builder.fs()
    fs.copy("build/package.json", "src/angular/package.json")
    
    wiz.response.status(200, res)
    
def list(segment):
    fs = wiz.project.fs("src", "angular")
    packagejson = fs.read.json("package.json")
    deps = packagejson['dependencies']
    res = []
    for dep in deps:
        res.append(dict(name=dep, version=deps[dep]))
    wiz.response.status(200, res)
