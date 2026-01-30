# WIZ Framework Architecture

## Overview

WIZ is a full-stack web development framework based on Python Flask, designed to easily integrate with Angular. It manages both backend and frontend together and provides an extensible IDE environment through a plugin-based architecture.

## Core Components

### 1. Framework Structure (season package)

```
season/
├── __init__.py          # Package initialization and main API exposure
├── cmd.py               # CLI command entry point
├── version.py           # Version information
├── command/             # CLI command implementation
│   ├── bundle.py        # Bundling commands
│   ├── create.py        # Project creation
│   ├── daemon.py        # Server execution and daemon management
│   ├── ide.py           # IDE commands
│   └── service.py       # System service management
├── lib/                 # Core library
│   ├── server.py        # Server class (Flask + SocketIO)
│   ├── core.py          # Wiz core functionality
│   ├── binding/         # HTTP and socket bindings
│   ├── static/          # Static resource management
│   └── ...
├── util/                # Utility functions
│   ├── cache.py
│   ├── compiler.py
│   ├── filesystem.py
│   ├── logger.py
│   └── string.py
└── data/                # Template data
    ├── ide/             # IDE source code
    ├── plugin/          # Plugin templates
    ├── sample/          # Sample projects
    └── websrc/          # Web source templates
```

### 2. Server Architecture

#### Server Class (`season.lib.server.Server`)

The core server class of the WIZ framework provides the following features:

```python
class Server:
    def __init__(self, path=None):
        self.boottime = time.time()
        self.package = season.lib.static.Package()
        self.path = season.lib.static.Path(path)
        self.config = season.lib.static.Config(server=self)
        self.cache = season.util.Cache()
        
        # Flask and SocketIO application initialization
        self.app.flask = Flask(...)
        self.app.socketio = SocketIO(...)
        
        # HTTP and socket bindings
        season.lib.binding.http(self)
        season.lib.binding.socket(self)
```

**Key Features:**
- **Flask Integration**: Basic web server functionality
- **SocketIO Integration**: Real-time bidirectional communication
- **Configuration Management**: `config.boot`-based configuration
- **Caching System**: Performance optimization
- **Wiz API**: Extended API through `wiz()` method

#### Project Structure

A created WIZ project has the following structure:

```
myapp/
├── config/              # Configuration files
│   ├── boot.py          # Server boot configuration
│   ├── ide.py           # IDE configuration
│   ├── service.py       # Service configuration
│   └── plugin.json      # Plugin configuration
├── public/              # Public directory
│   ├── app.py           # Application entry point
│   └── app.wsgi         # WSGI configuration
├── project/             # Projects directory
│   └── main/            # Main project
│       ├── config/      # Project configuration
│       ├── src/         # Source code
│       │   ├── app/     # Angular app components
│       │   ├── controller/ # Backend controllers
│       │   ├── model/   # Data models
│       │   ├── route/   # API routes
│       │   ├── portal/  # Portals (reusable modules)
│       │   ├── angular/ # Angular configuration
│       │   └── assets/  # Static assets
│       ├── build/       # Build output
│       └── bundle/      # Bundle files
├── ide/                 # WIZ IDE source
├── plugin/              # Plugins
│   ├── core/
│   ├── workspace/
│   ├── git/
│   └── utility/
└── wiz.pid              # Daemon process ID
```

### 3. Project Internal Structure (src/)

#### 3.1 App (Angular Components)

The `src/app/` directory contains Angular-based frontend components.

**Structure Example:**
```
src/app/
├── layout.empty/        # Layout component
│   ├── view.pug
│   ├── view.ts
│   ├── view.scss
│   └── app.json
└── page.main/           # Page component
    ├── view.pug         # Pug template
    ├── view.ts          # TypeScript logic
    ├── view.scss        # Stylesheet
    ├── app.json         # App metadata
    ├── api.py           # Backend API
    └── socket.py        # Socket handler
```

**app.json Example:**
```json
{
    "title": "/workflow",
    "mode": "page",
    "namespace": "main",
    "category": "general",
    "id": "page.main",
    "viewuri": "/workflow/**",
    "layout": "layout.empty",
    "ng": {
        "selector": "wiz-page-main",
        "inputs": [],
        "outputs": []
    }
}
```

**Component Types:**
- **Page**: Routable page components
- **Layout**: Layouts that wrap pages
- **Widget**: Reusable UI components

#### 3.2 Controller

The `src/controller/` directory defines the basic controllers for backend logic.

**base.py Example:**
```python
class Controller:
    def __init__(self):
        # Session initialization
        wiz.session = wiz.model("portal/season/session").use()
        sessiondata = wiz.session.get()
        wiz.response.data.set(session=sessiondata)
        
        # Internationalization
        lang = wiz.request.query("lang", None)
        if lang is not None:
            wiz.response.lang(lang)
            wiz.response.redirect(wiz.request.uri())
```

**Roles:**
- Session management
- Request/response handling
- Common logic implementation
- Authentication/authorization

#### 3.3 Model

The `src/model/` directory contains data models and business logic.

**Features:**
- Database abstraction
- Business logic encapsulation
- Reusable code structure

#### 3.4 Route

The `src/route/` directory defines API endpoints.

**Structure:**
```
src/route/
├── brand/
│   ├── app.json
│   └── controller.py
└── setting/
    ├── app.json
    └── controller.py
```

**controller.py Example:**
```python
segment = wiz.request.match("/brand/<action>/<path:path>")
action = segment.action

if action == "logo":
    # Logo handling logic
    fs = wiz.project.fs("bundle", "src", "assets", "brand")
    wiz.response.download(fs.abspath("logo.png"), as_attachment=False)

if action == "icon":
    # Icon handling logic
    wiz.response.download(fs.abspath("icon.ico"), as_attachment=False)

wiz.response.abort(404)
```

**Features:**
- RESTful API design
- URL pattern matching
- File download and upload
- JSON response handling

#### 3.5 Portal

The `src/portal/` directory contains reusable module packages.

**Structure:**
```
src/portal/
├── season/              # Portal package
│   ├── portal.json      # Metadata
│   ├── app/             # Angular components
│   ├── controller/      # Controllers
│   ├── model/           # Models
│   ├── route/           # Routes
│   └── libs/            # Libraries
└── dizest/
    └── ...
```

**portal.json Example:**
```json
{
    "package": "season",
    "title": "",
    "version": "2.0.0",
    "use_app": true,
    "use_widget": false,
    "use_route": true,
    "use_libs": true,
    "use_controller": true,
    "use_model": true
}
```

**Features:**
- Modularized functionality
- Reuse across projects
- Independent namespaces
- Selective feature activation

### 4. Configuration System

#### boot.py (Server Boot Configuration)

```python
# Bootstrap function
def bootstrap(app, config):
    pass

# Secret key
secret_key = "season-wiz-secret"

# SocketIO configuration
socketio = dict()
socketio['async_mode'] = 'threading'
socketio['cors_allowed_origins'] = '*'
socketio['async_handlers'] = True

# Server run configuration
run = dict()
run['host'] = "0.0.0.0"
run['port'] = 3000
run['use_reloader'] = False
```

**Configuration Items:**
- `bootstrap`: Function executed on server start
- `secret_key`: Flask session encryption key
- `socketio`: SocketIO server options
- `run`: Server execution options (host, port, etc.)

### 5. Plugin System

WIZ provides a powerful plugin architecture.

**Plugin Structure:**
```
plugin/
├── core/                # Core plugins
├── workspace/           # Workspace management
│   ├── app/
│   ├── command.py       # CLI commands
│   ├── filter.py
│   ├── model/
│   └── plugin.json
├── git/                 # Git integration
├── utility/             # Utilities
└── xterm/               # Terminal
```

**command.py Example:**
```python
def build(*args):
    if len(args) < 1:
        print("wiz command workspace build [projectName]")
        return
    
    project = args[0]
    wiz.project.checkout(project)
    builder = wiz.ide.plugin.model("builder")
    builder.build()
```

**Plugin Features:**
- Custom CLI commands
- IDE extensions
- Backend API additions
- Frontend widgets

### 6. IDE Integration

WIZ has a built-in web-based IDE that allows you to develop projects directly in the browser.

**IDE Structure:**
```
ide/
├── package.json
├── angular/             # Angular configuration
│   ├── angular.build.options.json
│   ├── index.html
│   ├── main.ts
│   ├── wiz.ts
│   └── wizbuild.js
├── app/                 # IDE app components
│   ├── core.app.ide/
│   ├── core.editor.monaco/
│   ├── workspace.app.explore/
│   └── ...
└── assets/
```

**Key Features:**
- File explorer
- Code editor (Monaco Editor)
- Terminal
- Git integration
- Real-time preview

### 7. Build System

WIZ automatically builds Angular projects.

**Build Process:**
1. TypeScript compilation
2. Pug template conversion
3. SCSS compilation
4. Angular bundling
5. Optimization and compression

**Build Command:**
```bash
wiz command workspace build main
```

### 8. Communication Architecture

#### HTTP Communication
- RESTful API
- JSON request/response
- File upload/download

#### WebSocket Communication (SocketIO)
- Real-time bidirectional communication
- Event-based messaging
- Namespace support

**Socket Handler Example (socket.py):**
```python
def connect():
    # On client connection
    pass

def disconnect():
    # On client disconnection
    pass

def on_message(data):
    # On message reception
    wiz.response.send({"result": "ok"})
```

## Data Flow

### 1. HTTP Request Flow

```
Browser → Flask Router → Controller → Model → Response
                ↓
            Route (API)
                ↓
            App (API Handler)
```

### 2. Page Rendering Flow

```
URL Request → Route Matching → Layout Load → Page Component Load
                                                    ↓
                                            Angular Rendering
                                                    ↓
                                            API Calls (api.py)
```

### 3. Socket Communication Flow

```
Client Event → SocketIO Namespace → socket.py Handler → Response
                                           ↓
                                      Business Logic
```

## Scalability

### 1. Horizontal Scaling
- Multi-process support
- Load balancing capable

### 2. Vertical Scaling
- Adding features through plugins
- Module reuse through portal system
- Custom component development

### 3. Integration
- WSGI standard support
- Compatible with various web servers (Nginx, Apache, etc.)
- Container support (Docker)

## Security

### 1. Session Management
- Flask session-based
- Secret key encryption

### 2. CORS Configuration
- SocketIO CORS support
- Domain-based access control

### 3. Authentication/Authorization
- Custom authentication system implementation possible
- Session-based permission management

## Performance Optimization

### 1. Caching
- Server-level cache (`season.util.Cache`)
- Static file caching

### 2. Bundling
- Angular AOT compilation
- Code splitting
- Compression and minification

### 3. Asynchronous Processing
- SocketIO async handlers
- Multithreading support

## Conclusion

WIZ is a full-stack framework that integrates Flask and Angular with the following characteristics:

- **Integrated Development Environment**: Manage backend and frontend in one project
- **Plugin Architecture**: Extensible and modularized structure
- **Web-based IDE**: Develop directly in the browser
- **Real-time Communication**: Bidirectional communication through SocketIO
- **Easy Deployment**: Project management and service registration through CLI

Through this architecture, WIZ supports fast and efficient web application development.
