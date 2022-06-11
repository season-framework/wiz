# SEASON WIZ Framework

- SEASON WIZ is framework & IDE for web development.
- SEASON WIZ Support git flow

![screenshot](https://github.com/season-framework/wiz/blob/main/screenshot/wiz.gif)

## Installation

```bash
pip install season             # install
pip install season --upgrade   # upgrade lastest
```

## Usage

- create project

```bash
cd <workspace>
wiz create myapp
cd myapp
wiz run
```

> `http://127.0.0.1:3000/wiz` on your web browser

- create from git repo

```bash
wiz create myapp --uri=https://your-custom/git/project
```

- cleaning cache

```bash
wiz clean
```

- update ide

```bash
wiz update ide  # update to default ide
wiz update ide --uri=https://your-custom/git/ide/project
```


## Upgrade project from old wiz (under 0.5.x)

- transform structure

```
cd <project-path>
wiz upgrade
```

- in theme, change methods like before

```
# wiz.theme('default', 'base', 'header.pug')
wiz.theme('default').layout('base').view('header.pug')
```

- compiler update, `javascript.py` 

```python
def compile(wiz, js, data):
    if 'render_id' not in data:
        return js

    app_id = data['app_id']
    render_id = data['render_id']
    namespace = data['namespace']

    o = "{"
    e = "}"
    kwargsstr = "{$ kwargs $}"
    dicstr = "{$ dicstr $}"
    branch = wiz.branch()

    js = f"""
    function __init_{render_id}() {o}
        let wiz = season_wiz.load('{app_id}', '{namespace}', '{render_id}');
        wiz.branch = '{branch}';
        wiz.data = wiz.kwargs = wiz.options = JSON.parse(atob('{kwargsstr}'));
        wiz.dic = wiz.DIC = JSON.parse(atob('{dicstr}'));
        
        {js};

        try {o}
            app.controller('{render_id}', wiz_controller); 
        {e} catch (e) {o} 
            app.controller('{render_id}', ()=> {o} {e} ); 
        {e} 
    {e}; 
    __init_{render_id}();
    """

    return js
```

- compiler update, `html.py`

```python
def compile(wiz, html, data):
    if 'render_id' not in data:
        return html
        
    app_id = data['app_id']
    render_id = data['render_id']
    namespace = data['namespace']

    html = html.split(">")
    if len(html) > 1:
        html = html[0] + f" id='{render_id}' ng-controller='{render_id}'>" + ">".join(html[1:])
    else:
        html = f"<div id='{render_id}' ng-controller='{render_id}'>" + ">".join(html) + "</div>"

    return html
```

- config file update

```python
## old version
from season import stdClass
config = stdClass()
config.path = "/var/www/wiki/data"

## new version
path = "/var/www/wiki/data"
```


## Release Note

### 1.0.3

- WSGI Bug Fixed

### 1.0.2

- remove dukpy (windows install bug)

### 1.0.1

- support macosx

### 1.0.0

- clean code
- full changed ide
- remove season-flask concept
- enhanced performance
- logging for wiz concept
- upgrade plugin structure
- config structure changed
- stable version for git merge

### 0.5.x

- support plugin storage
- port scan when wiz project created
- wiz based online plugin development env
- support programmable api for plugins
- remove useless resources
- socketio config (config/socketio.py)
- packages version bug fixed (jinja2, werkzeug)
- add src folder for tracing plugin code
- check installed function (wiz.installed())
- forced dev mode in dev branch (if not master)
- wiz `resource_handler` updated
- add function response(flask_resp) and pil_image at `response`
- add babel script option
- add `wiz.path()` function
- git merge bug fixed
- update wiz theme render logic
- git merge logic changed
- wiz instance as global in wiz api
- add `match` api at wiz instance

### 0.4.x

- Integrate WIZ & Season Flask
- support git flow
- workspace structure changed
- base code workspace changed (mysql to filesystem)
- UI upgrade
- support installer
- developer/production mode
    - developer: enabled socketio logger on every pages
    - production: disabled socketio logger
- dictionary bug fixed in App HTML
- history display ui changed (workspace)
- app browse in route workspace
- add cache clean in workspace
- git bug changed (if author is not set, default user to `wiz`)
- full size log viewer
- keyword changed
- cache bug fixed
- socketio performance upgrade 
- wiz.js embeded
- WIZ API (js) changed (async mode)

### 0.3.x

- add socket.io 
- framework on build
- command run modified (add pattern, ignores)
- change Framework Object

### 0.2.x

- framework structure upgraded
- command line tool function changed
- submodule structure added
- logging 
- simplify public directory structure
- add response.template_from_string function
- add response.template function
- add variable expression change option
- interface loader update
- config onerror changed 
- add response.abort
- error handler in controller `__error__`
- response redirect update (relative module path)
- logger upgrade (file trace bug fixed)
- logger upgrade (log executed file trace)
- logger upgrade (code trace)
- error handler bug fixed
- apache wsgi bug fixed (public/app.py)
- apache wsgi bug fixed
