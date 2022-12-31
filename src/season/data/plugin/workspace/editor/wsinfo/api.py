import git as Git
import os
import zipfile
import tempfile
import time
import shutil
import datetime
import json

workspace = wiz.workspace("service")
working_dir = wiz.server.path.branch
fs = workspace.fs(os.path.join(working_dir))

def git():
    path = wiz.request.query("path", True)
    target_path = fs.abspath(os.path.join(path))
    repo = Git.Repo.init(target_path)
    
    resp = dict()

    author = dict()
    try: author['name'] = repo.config_reader().get_value("user", "name")
    except: author['name'] = 'wiz'
    try: author['email'] = repo.config_reader().get_value("user", "email")
    except: author['email'] = 'wiz@localhost'
    resp['author'] = author
    resp['remote'] = [x.name for x in repo.remotes]
    
    wiz.response.status(200, resp)

def git_update():
    path = wiz.request.query("path", True)
    name = wiz.request.query("name", None)
    email = wiz.request.query("email", None)

    target_path = fs.abspath(os.path.join(path))
    repo = Git.Repo.init(target_path)

    if name is not None:
        repo.config_writer().set_value("user", "name", name).release()
    if email is not None:
        repo.config_writer().set_value("user", "email", email).release()

    wiz.response.status(200)

def rebuild():
    path = wiz.request.query("path", True)
    current_branch = wiz.branch()
    wiz.branch(path)
    wp = wiz.workspace("service")
    wp.build.clean()
    wp.build()
    wiz.branch(current_branch)
    wiz.response.status(200)

def delete():
    path = wiz.request.query("path", True)
    fs.delete(path)
    wiz.response.status(200)