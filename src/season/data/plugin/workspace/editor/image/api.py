import os

def read(segment):
    fs = wiz.project.fs()
    path = segment.path
    ext = os.path.splitext(path)[-1]

    if ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'ico']:
        wiz.response.status(401)    

    if fs.isfile(path):
        path = fs.abspath(path)
        wiz.response.download(path, as_attachment=False)

    wiz.response.status(404)
