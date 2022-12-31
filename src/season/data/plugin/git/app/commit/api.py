import git
import os

gitignore = """cache/
config/
.vscode/
test/

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/
"""

workspace = wiz.workspace("service")
cwd = workspace.fs().abspath()
repo = git.Repo.init(cwd)

def reset():
    gitfile = wiz.request.query("file", None)
    try:
        if gitfile is None or len(gitfile) == 0:
            repo.git.reset()
        else:
            repo.git.reset(gitfile)
    except:
        pass
    wiz.response.status(200)

def add():
    gitfile = wiz.request.query("file", None)
    try:
        if gitfile is None or len(gitfile) == 0:
            repo.git.add('--all')
        else:
            repo.git.add(gitfile, update=True)
    except:
        pass
    wiz.response.status(200)

def changes():
    res = dict(staged=[], unstaged=[])

    try:
        tags = repo.commit('HEAD').diff(None)
        fmap = dict()
        for diff in tags:
            fmap[diff.b_path] = diff.change_type

        staged = repo.index.diff("HEAD")
        for diff in staged:
            obj = {"change_type": fmap[diff.b_path], "path": diff.b_path}   
            path = obj['path']
            res['staged'].append(obj)

        unstaged = repo.index.diff(None)
        for diff in unstaged:
            obj = {"change_type": fmap[diff.b_path], "path": diff.b_path}        
            path = obj['path']
            res['unstaged'].append(obj)
    except Exception as e:
        workspace.fs().write(".gitignore", gitignore)
        repo.git.add('--all')
        repo.index.commit("init")
        
    wiz.response.status(200, res)

def commit():
    try:
        message = wiz.request.query("message", "commit")
        repo.index.commit(message)
    except Exception as e:
        wiz.response.status(500, str(e))
    wiz.response.status(200)