import os

def read():
    workspace = wiz.workspace("service")
    fs = workspace.fs()

    path = wiz.request.query("path", True)
    ext = path.split('.')[-1]
    if ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'ico']:
        if os.path.isfile(fs.abspath(path)):
            path = fs.abspath(path)
            wiz.response.download(path, as_attachment=False)

    wiz.response.status(404)
