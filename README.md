# WIZ IDE

- WIZ is IDE for web development
- Using angular more easy

![screenshot](https://github.com/season-framework/wiz/blob/main/screenshot/wiz.gif)

## Installation

- install nodejs, npm, angular

```bash
apt install nodejs npm
npm i -g n
n stable
```

- install wiz python package

```bash
pip install season             # install
pip install season --upgrade   # upgrade lastest
```

## Usage

- create project and start web server

```bash
cd <workspace>
wiz create myapp
cd myapp
wiz run --port 3000
# `http://127.0.0.1:3000/wiz` on your web browser
```

- start server as daemon

```bash
wiz server start # start daemon server
wiz server stop  # stop daemon server
```

- regist system service for linux

```bash
# run on wiz project root directory
wiz service regist myapp
wiz service start myapp
```

- upgrade ide from command line

```bash
pip install season --upgrade # upgrade core
wiz ide upgrade # ide upgrade
```

## WIZ CLI

### Create Project
- `wiz create [Project Name]`
    - Example
        ```bash
        wiz create myapp
        ```

### plugin commands
- `wiz command <plugin name> args`
    - Example
        ```bash
        wiz command workspace build main
        ```

### Daemon API
- `wiz run --host=<host> --port=<port> --log=<log file path>`
    - Flag
        | Flag | Syntax | Description |
        |---|---|---|
        | --port | wiz run [action] --port=PORT | Web server port, Default 3000 |
        | --host | wiz run [action] --host=HOST | Web server host, Default 0.0.0.0 |
        | --log | wiz run [action] --log=PATH | Log file path, Default None |
    - Example
        ```bash
        wiz run --port=3000
        wiz run --port=3000 --host=0.0.0.0
        wiz run --port 3000 --log wiz.log
        ```

- `wiz server [action] --log=<log file path> --force`
    - Action
        | Action | Syntax | Description |
        |---|---|---|
        | start | wiz server start [flags] | Start wiz server as daemon |
        | stop | wiz server stop [flags] | Stop wiz server daemon |
        | restart | wiz server restart [flags] | Restart wiz server daemon |
    - Flag
        | Flag | Syntax | Description |
        |---|---|---|
        | --log | wiz server [action] --log=PATH | Log file path, Default None |
        | --force | wiz server start --force | Force start daemon |
    - Example
        ```bash
        wiz server start --force
        wiz server stop
        wiz server restart
        ```

### Service API
- `wiz service list`
    - Example
        ```bash
        wiz service list
        ```

- `wiz service regist [name] [port]`
    - Same AS
        - `install`
    - Example
        ```bash
        wiz service regist myapp
        # or
        wiz service install myapp src 3001
        # or
        wiz service install myapp bundle 3001
        ```

- `wiz service unregist [name]`
    - Same AS
        - `uninstall`, `remove`, `delete`, `rm`
    - Example
        ```bash
        wiz service unregist myapp
        # or
        wiz service remove myapp
        ```

- `wiz service status [name]`
    - Example
        ```bash
        wiz service status myapp
        ```

- `wiz service start [name]`
    - Example
        ```bash
        wiz service start myapp
        wiz service start # start all services
        ```

- `wiz service stop [name]`
    - Example
        ```bash
        wiz service stop myapp
        wiz service stop  # stop all services
        ```

- `wiz service restart [name]`
    - Example
        ```bash
        wiz service restart myapp
        wiz service restart  # restart all services
        ```

### Bundle Project
- `wiz bundle --project=<Project Name>`
    - Example
        ```bash
        wiz bundle # bundle main project
        wiz bundle --project=main
        ```
    - Output
        - `<workspace>/bundle` file created after run bundle api
        - run using command `wiz run --bundle`
        - or adding services using `wiz service install <myservice> bundle`

## Version Policy

> x.y.z

- `x`: major update
    - upgrade not supported
- `y`: minor update
    - support command upgrade
    - core function changed
    - required server restart
- `z`: ui update
    - support upgrade from web ui
    - not required server restart

## Release Note

### 2.4.1

- [core] fixed library path not included error

### 2.4.0

- [core] upgrade to flask 3
- [core] enhanced 3rd-party plugin concept
- [core] `branch` renamed as `project` 
- [core] util function structure changed (eg. `season.util.os.FileSystem` to `season.util.fs`)
- [core] support plugin command (3rd-party command)
- [core] support plugin filter (customized route)
- [core] project and ide structure changed
- [core] remove `workspace` object (changed to `wiz.project` or `wiz.ide`)
- [plugins] update wiz api changes

### 2.3.x

- major issues
    - move build logic to ide plugin
    - add bundle structure
    - localize angular cli
    - add linux service cli
    - add statusbar at bottom of ide
- [core] move build logic to ide plugin
- [core] add bundle structure
- [core] localize angular cli
- [core] add linux service cli
- [core] add statusbar at bottom of ide
- [plugin] define `model` at plugin
- [plugin/workspace] angular build logic changed
- [plugin/workspace] integrated portal framework plugin at workspace
- [plugin/workspace] build portal framework on builder model
- [plugin/workspace] portal framework controller bug fixed
- [plugin/workspace] portal framework editore in command
- [plugin/core] update auto complete in monaco editor
- [core] upgrade to `angular 17`
- [core] cache bug fixed (conflict branch)
- [core] command change (bundle -> pkg)
- [core] change requirement for python old version support
- [plugin/workspace] create widget bug at portal module fixed
- [core] add dependency (flask-socketio)
- [core] upgrade to `angular 16`
- [core] color changed
- [core] add build command
- [plugin/workspace] tree view component changed
- [plugin/git] commit bug fixed
- [core] wiz.response stream api
- [plugin/workspace] bug at app create fixed
- [core] cache added for wiz config
- [core] cache added for wiz components (model, controller, api)
- [core] bundle command added
- [core] service command upgraded (add bundle option)
- [core] service command upgraded (add port option)
- [core] boot config changed
- [core] boot config changed
- [plugin/workspace] portal framework widget create bug fixed
- [plugin/workspace] statusbar bug fixed
- [plugin/workspace] npm plugin bug fixed
- [core] default plugin config bug fixed (portal framework)
- [core] assets path bug fixed
- [core] bundle path bug fixed
- [plugin/workspace] config list bug fixed
- [plugin/workspace] app.json bug fixed

### 2.2.x

- major issues
    - ide overlay menu
    - shortcut config (plugin & user customized)
- [plugin/portal] add portal framework plugin
- [plugin/workspace] refresh list bug fixed
- [core] ide monaco editor bug fixed
- [plugin/workspace] Usability improvements
- [plugin/core] Auto Complete keyword
- [core] toastr on build error 
- [plugin/workspace] hidden portal framework on route
- [plugin/workspace] image viewer
- [core] angular version upgrade
- [core] typescript dependencies bug fixed

### 2.1.x

- major issues
    - ide plugin concept changed
    - ide layout changed
    - ide config concept added
- [plugin/core] move to app link in monaco editor
- [plugin/core] add core plugins upgrade button
- [plugin/core] add restart server button
- [plugin/workspace] add app/route editor service
- [plugin/workspace] preview bug fixed
- [plugin/workspace] page namespace bug fixed
- [plugin/workspace] set default code if component.ts not exists
- [plugin/workspace] import & create app bug fixed
- [plugin/core] remove useless log
- [plugin/workspace] config folder bug fixed
- [plugin] bug fixed (remove unused file)
- [plugin/workspace] add route build
- [plugin/workspace] remove useless log
- [plugin] `core` plugin updated
- [core] add `lib/plugin` object
- [command] bug fixed

### 2.0.x

- major issues
    - upgrade base project to angular 14.2.0
    - UI/UX full changed
    - Drag and Drop Interface
    - git branch to project (multiple project in workspace)
    - Enhanced IDE Plugin and easily develop 3rd party apps
    - support pip and npm on ui
- ide socket
- auto install `@angular/cli`
- angular 15
- flask response bug fixed (on filesend)
- wiz bundle mode
- update wiz server command (multiprocess)
- config bug fixed
- socketio bug fixed (ide controller)
- threading bug fixed (flask, socketio)

### 1.0.x

- major issue
    - clean code
    - full changed ide
    - remove season-flask concept
    - enhanced performance
    - logging for wiz concept
    - upgrade plugin structure
    - config structure changed
    - stable version for git merge
- add `wiz server start --log <file>` method 
- print bug fixed
- add daemon server command
- Socket.IO transport
- server starting log
- auto remove invalid character on update
- WSGI Bug Fixed
- remove dukpy (windows install bug)
- support macosx

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
