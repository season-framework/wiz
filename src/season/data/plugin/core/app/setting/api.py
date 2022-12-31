import os

workspace = wiz.workspace()
fs = workspace.fs("..", "config")

def load():
    path = wiz.request.query("path", True)
    wiz.response.status(200, fs.read(path, ""))

def update(segment):
    path = wiz.request.query("path", True)
    code = wiz.request.query("code", True)
    fs.write(path, code)
    wiz.server.config.clean()
    wiz.response.status(200)

def build():
    workspace.build()
    wiz.response.status(200)