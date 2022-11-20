# WIZ Framework

- WIZ is IDE for web development
- Using angular more easy

![screenshot](https://github.com/season-framework/wiz/blob/main/screenshot/wiz.gif)

## Installation

- install nodejs, npm, angular

```bash
apt install nodejs npm
npm i -g n
n stable
npm install -g @angular/cli@14.2.3
```

- install wiz python package

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
wiz run --port 3000
```

> `http://127.0.0.1:3000/wiz` on your web browser

- create from git repo

```bash
wiz create myapp --uri=https://your-custom/git/project
```

- daemon server

```bash
wiz server start # start daemon server
wiz server stop  # stop daemon server
```

## Release Note

### 2.0.5

- wiz bundle mode

### 2.0.4

- update wiz server command (multiprocess)

### 2.0.3

- config bug fixed

### 2.0.2

- socketio bug fixed (ide controller)

### 2.0.1

- threading bug fixed (flask, socketio)

### 2.0.0

- upgrade base project to angular 14.2.0
- UI/UX full changed
- Drag and Drop Interface
- git branch to project (multiple project in workspace)
- Enhanced IDE Plugin and easily develop 3rd party apps
- support pip and npm on ui

### 1.0.7

- add `wiz server start --log <file>` method 

### 1.0.6

- print bug fixed

### 1.0.5

- add daemon server command

### 1.0.4

- Socket.IO transport
- server starting log
- auto remove invalid character on update

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
