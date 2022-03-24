# SEASON WIZ Framework

- SEASON WIZ is framework & IDE for web development.
- SEASON WIZ Support git flow

## Installation

```bash
pip install season
```

## Usage

- create project

```
cd <workspace>
wiz create myapp
cd myapp
wiz run
```

- `127.0.0.1:3000/wiz` on your web browser

- cleaning cache and init plugins

```
cd <workspace>
wiz clean
```


## Roadmap

- git flow
    - support management for remote branches

## Release Note

### 0.5.28

- core render bug fixed
- add src folder for tracing plugin code

### 0.5.27

- Response PIL Bug fixed

### 0.5.26

- plugin menu bug fixed (cache bug)

### 0.5.25

- check installed function (wiz.installed())
- forced dev mode in dev branch (if not master)

### 0.5.24

- wiz `resource_handler` updated

### 0.5.23

- add function response(flask_resp) and pil_image at `response`

### 0.5.22

- `request` file api changed

### 0.5.21

- change babel script option to extendable script option

### 0.5.20

- add babel script option


### 0.5.19

- add `wiz.path()` function

### 0.5.18

- git merge bug fixed

### 0.5.17

- update wiz theme render logic

### 0.5.16

- git merge logic changed

### 0.5.15

- public directory bug fixed (wiz)

### 0.5.14

- app.py bug fixed

### 0.5.13

- app.py bug fixed

### 0.5.12

- app.py bug fixed

### 0.5.11

- render id bug fixed


### 0.5.10

- json dumps bug fixed

### 0.5.9

- git merge bug fixed


### 0.5.8

- wiz instance as global in wiz api

### 0.5.7

- bug fixed in theme function

### 0.5.6

- bug fixed in theme function

### 0.5.5

- add `match` api at wiz instance

### 0.5.4

- api error logger bug fixed

### 0.5.3

- support plugin storage

### 0.5.2

- route bug fixed

### 0.5.1

- port scan when wiz project created

### 0.5.0

- wiz based online plugin development env
- support programmable api for plugins
- remove useless resources

### 0.4.8

- scroll bug fixed in logger


### 0.4.7

- scroll bug fixed in logger

### 0.4.6

- dictionary bug fixed in App HTML
- history display ui changed (workspace)
- app browse in route workspace

### 0.4.5

- cache bug fixed
- add cache clean in workspace

### 0.4.4

- git bug changed (if author is not set, default user to `wiz`)

### 0.4.3

- full size log viewer
- keyword changed
- cache bug fixed
- socketio performance upgrade 

### 0.4.2

- wiz.js embeded
- developer/production mode
    - developer: enabled socketio logger on every pages
    - production: disabled socketio logger

### 0.4.1

- WIZ API (js) changed (async mode)

### 0.4.0

- Integrate WIZ & Season Flask
- support git flow
- workspace structure changed
- base code workspace changed (mysql to filesystem)
- UI upgrade
- support installer

### 0.3.12

- framework on build

### 0.3.11

- socketio error display

### 0.3.10

- socket bug fixed

### 0.3.9

- command run modified (add pattern, ignores)

### 0.3.7

- change Framework Object

### 0.3.6

- Socket.io disconnect bug fixed

### 0.3.3

- Socket.io Namespace Injection

### 0.3.2

- Socket.io bug fixed

### 0.3.1

- Socket.io bug fixed


### 0.3.0

- add Socket.io 


### 0.2.14

- add response.template_from_string function

### 0.2.13

- add response.template function

### 0.2.12

- add variable expression change option

### 0.2.11

- interface loader update


### 0.2.10

- config onerror changed 

### 0.2.9

- add response.abort

### 0.2.8

- error handler in controller `__error__`

### 0.2.7

- response redirect update (relative module path)

### 0.2.6

- logger upgrade (file trace bug fixed)

### 0.2.5

- logger upgrade (log executed file trace)

### 0.2.4

- logger upgrade (code trace)

### 0.2.3

- error handler bug fixed

### 0.2.2

- apache wsgi bug fixed (public/app.py)

### 0.2.1

- apache wsgi bug fixed

### 0.2.0

- framework structure upgraded
- command line tool function changed
- submodule structure added
- logging 
- simplify public directory structure

