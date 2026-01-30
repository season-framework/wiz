# WIZ Framework Usage Guide

## Table of Contents
1. [Installation](#installation)
2. [Project Creation](#project-creation)
3. [Project Structure](#project-structure)
4. [Server Execution](#server-execution)
5. [Page Creation](#page-creation)
6. [Component Development](#component-development)
7. [API Development](#api-development)
8. [Adding Routes](#adding-routes)
9. [Writing Models](#writing-models)
10. [Using Portals](#using-portals)
11. [Build and Deployment](#build-and-deployment)

---

## Installation

### 1. System Requirements

- Python 3.8 or higher
- Node.js and npm
- Angular CLI

### 2. Installing Node.js and npm

```bash
# Install Node.js and npm
apt install nodejs npm

# Install latest version through n package
npm i -g n
n stable

# Remove old version
apt purge nodejs npm
```

### 3. Installing WIZ Framework

```bash
# Install
pip install season

# Upgrade
pip install season --upgrade
```

### 4. Verify Installation

```bash
wiz --version
```

---

## Project Creation

### 1. Create New Project

```bash
# Navigate to workspace directory
cd <workspace>

# Create project
wiz create myapp

# Navigate to project directory
cd myapp
```

### 2. Generated Project Structure

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
├── project/             # Projects directory (empty)
├── ide/                 # WIZ IDE source
├── plugin/              # Plugins
│   ├── core/
│   ├── workspace/
│   ├── git/
│   └── utility/
└── wiz.pid              # Daemon process ID (created when running)
```

---

## Project Structure

In WIZ, the actual application is created under the `project/` directory. By default, it's recommended to create a `main` project.

### Project Internal Structure (project/main/)

```
project/main/
├── config/              # Project configuration (optional)
├── src/                 # Source code
│   ├── app/             # Angular app components
│   │   ├── layout.empty/    # Layout component
│   │   │   ├── view.pug
│   │   │   ├── view.ts
│   │   │   ├── view.scss
│   │   │   └── app.json
│   │   └── page.main/       # Page component
│   │       ├── view.pug     # Pug template
│   │       ├── view.ts      # TypeScript logic
│   │       ├── view.scss    # Stylesheet
│   │       ├── app.json     # App metadata
│   │       ├── api.py       # Backend API (optional)
│   │       └── socket.py    # Socket handler (optional)
│   ├── controller/      # Backend controllers
│   │   └── base.py      # Base controller
│   ├── model/           # Data models
│   ├── route/           # API routes
│   │   ├── brand/
│   │   │   ├── app.json
│   │   │   └── controller.py
│   │   └── setting/
│   ├── portal/          # Portals (reusable modules)
│   │   ├── season/
│   │   │   ├── portal.json
│   │   │   ├── app/
│   │   │   ├── controller/
│   │   │   ├── model/
│   │   │   └── route/
│   │   └── ...
│   ├── angular/         # Angular configuration
│   └── assets/          # Static assets
├── build/               # Build output (auto-generated)
├── bundle/              # Bundle files (auto-generated)
├── package.json         # npm package configuration
└── node_modules/        # npm dependencies
```

---

## Server Execution

### 1. Running in Development Mode

```bash
# Default run (port 3000)
wiz run

# Specify port
wiz run --port=3000

# Specify host and port
wiz run --port=3000 --host=0.0.0.0

# Specify log file
wiz run --port=3000 --log=wiz.log
```

### 2. Running in Daemon Mode

```bash
# Start daemon
wiz server start

# Stop daemon
wiz server stop

# Restart daemon
wiz server restart

# Specify log file
wiz server start --log=wiz.log
```

### 3. Register as System Service (Linux)

```bash
# Register service
wiz service regist myapp

# Start service
wiz service start myapp

# Stop service
wiz service stop myapp

# Check service status
wiz service status myapp
```

### 4. Access IDE

After running the server, access this URL in browser:

```
http://127.0.0.1:3000/wiz
```

---

## Page Creation

### 1. Creating via WIZ IDE

1. Access `http://127.0.0.1:3000/wiz` in browser
2. Right-click on `project/main/src/app` directory in left file explorer
3. Select "New Page"
4. Enter page name (e.g., `page.dashboard`)

### 2. Manual Creation

#### 2.1 Create Directory

```bash
cd project/main/src/app
mkdir page.dashboard
```

#### 2.2 Create Required Files

**app.json** - Page metadata
```json
{
    "title": "Dashboard",
    "mode": "page",
    "namespace": "main",
    "category": "general",
    "id": "page.dashboard",
    "ng.build": {
        "id": "page.dashboard",
        "name": "PageDashboardComponent",
        "path": "./page.dashboard/page.dashboard.component"
    },
    "viewuri": "/dashboard/**",
    "layout": "layout.empty",
    "preview": "/dashboard",
    "ng": {
        "selector": "wiz-page-dashboard",
        "inputs": [],
        "outputs": []
    },
    "template": "wiz-page-dashboard()",
    "controller": ""
}
```

**view.ts** - TypeScript logic
```typescript
import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public async ngOnInit() {
        await this.service.init();
        await this.service.render();
    }

    public async load() {
        // Data loading logic
    }
}
```

**view.pug** - Pug template
```pug
.container
    h1 Dashboard
    p Welcome to the dashboard!
```

**view.scss** - Stylesheet
```scss
.container {
    padding: 20px;
    
    h1 {
        color: #333;
    }
}
```

#### 2.3 API Handler (Optional)

**api.py** - Backend API
```python
# Handle GET request
def load():
    data = {"message": "Hello from API"}
    wiz.response.status(200, data)

# Handle POST request
def save():
    data = wiz.request.query()
    # Data processing logic
    wiz.response.status(200, {"result": "success"})
```

**socket.py** - WebSocket handler
```python
def connect():
    """On client connection"""
    print("Client connected")

def disconnect():
    """On client disconnection"""
    print("Client disconnected")

def on_message(data):
    """On message reception"""
    wiz.response.send({"echo": data})
```

### 3. Access Page

After building, access this URL:
```
http://127.0.0.1:3000/dashboard
```

---

## Component Development

### 1. Creating Layout Component

Layouts are common structures that wrap pages.

**app.json**
```json
{
    "mode": "layout",
    "id": "layout.default",
    "ng.build": {
        "id": "layout.default",
        "name": "LayoutDefaultComponent",
        "path": "./layout.default/layout.default.component"
    }
}
```

**view.pug**
```pug
.layout
    header
        h1 My Application
        nav
            a(href="/") Home
            a(href="/dashboard") Dashboard
    
    main
        router-outlet
    
    footer
        p © 2026 My Application
```

### 2. Creating Widget Component

Reusable UI components.

**app.json**
```json
{
    "mode": "widget",
    "id": "widget.button",
    "ng": {
        "selector": "wiz-widget-button",
        "inputs": ["label", "color"],
        "outputs": ["onClick"]
    }
}
```

**view.ts**
```typescript
import { Input, Output, EventEmitter } from '@angular/core';

export class Component {
    @Input() label: string = "Click me";
    @Input() color: string = "primary";
    @Output() onClick = new EventEmitter();

    public handleClick() {
        this.onClick.emit();
    }
}
```

**view.pug**
```pug
button.btn([class]="'btn-' + color", (click)="handleClick()")
    | {{ label }}
```

### 3. Using Components

Using widget in other components:

```pug
wiz-widget-button(
    [label]="'Submit'",
    [color]="'success'",
    (onClick)="onSubmit()"
)
```

---

## API Development

### 1. Component API (api.py)

You can create a component-specific API by creating `api.py` in each page/widget directory.

**project/main/src/app/page.dashboard/api.py**
```python
# GET /api/page.dashboard/users
def users():
    users = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
    wiz.response.status(200, users)

# POST /api/page.dashboard/user
def user():
    data = wiz.request.query()
    name = data.get("name", "")
    
    # Database save logic
    user_id = 123
    
    wiz.response.status(200, {
        "id": user_id,
        "name": name
    })

# File upload
def upload():
    files = wiz.request.files()
    for filename in files:
        file = files[filename]
        # File save logic
        fs = wiz.project.fs("data", "uploads")
        fs.write(filename, file.read())
    
    wiz.response.status(200, {"result": "success"})

# File download
def download():
    fs = wiz.project.fs("data", "uploads")
    filepath = fs.abspath("sample.pdf")
    wiz.response.download(filepath, as_attachment=True)
```

### 2. Calling API from Frontend

**view.ts**
```typescript
export class Component {
    constructor(public service: Service) { }

    public async loadUsers() {
        // GET request
        let res = await this.service.api.call("users");
        console.log(res.data); // [{id: 1, name: "Alice"}, ...]
    }

    public async createUser() {
        // POST request
        let data = { name: "Charlie" };
        let res = await this.service.api.call("user", data);
        console.log(res.data); // {id: 123, name: "Charlie"}
    }

    public async uploadFile(event) {
        let files = event.target.files;
        let formData = new FormData();
        formData.append("file", files[0]);
        
        let res = await this.service.api.call("upload", formData);
        console.log(res.data);
    }
}
```

### 3. wiz Object API

Main `wiz` APIs available in **api.py**:

```python
# Request data
data = wiz.request.query()           # GET/POST parameters
data = wiz.request.query("key", default)  # Get specific key
files = wiz.request.files()          # Uploaded files
segment = wiz.request.match("/users/<id>")  # URL pattern matching

# Response
wiz.response.status(200, data)       # JSON response
wiz.response.download(path)          # File download
wiz.response.redirect(url)           # Redirect
wiz.response.abort(404)              # HTTP error

# Filesystem
fs = wiz.project.fs("data")          # Project filesystem
fs = wiz.fs()                        # Current component filesystem
data = fs.read("file.txt")           # Read file
fs.write("file.txt", data)           # Write file
fs.read.json("data.json")            # Read JSON

# Model
model = wiz.model("portal/season/session")
instance = model.use()

# Session
wiz.session.set("key", "value")
value = wiz.session.get("key")
```

---

## Adding Routes

Routes provide independent API endpoints.

### 1. Creating Route

**project/main/src/route/api/app.json**
```json
{
    "id": "api",
    "uri": "/api"
}
```

**project/main/src/route/api/controller.py**
```python
import season
import json

# Get URL segments
segment = wiz.request.match("/api/<action>/<path:path>")
action = segment.action
path = segment.path

if action == "users":
    # Handle /api/users/...
    users = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
    wiz.response.status(200, users)

elif action == "posts":
    # Handle /api/posts/...
    posts = [
        {"id": 1, "title": "Hello World"},
        {"id": 2, "title": "WIZ Framework"}
    ]
    wiz.response.status(200, posts)

# 404 error
wiz.response.abort(404)
```

### 2. Accessing Route

```
GET http://127.0.0.1:3000/api/users
GET http://127.0.0.1:3000/api/posts
```

### 3. Advanced Routing

**RESTful API example:**

```python
segment = wiz.request.match("/api/<resource>/<int:id>")
resource = segment.resource
resource_id = segment.id

method = wiz.request.request().method

if resource == "users":
    if method == "GET":
        # Retrieve user
        user = get_user_by_id(resource_id)
        wiz.response.status(200, user)
    
    elif method == "POST":
        # Create user
        data = wiz.request.query()
        user_id = create_user(data)
        wiz.response.status(201, {"id": user_id})
    
    elif method == "PUT":
        # Update user
        data = wiz.request.query()
        update_user(resource_id, data)
        wiz.response.status(200, {"result": "success"})
    
    elif method == "DELETE":
        # Delete user
        delete_user(resource_id)
        wiz.response.status(204)
```

---

## Writing Models

Models encapsulate business logic and data access.

### 1. Creating Model File

**project/main/src/model/user.py**
```python
import season

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.db = self.wiz.model("portal/season/db").use()
    
    def get_users(self):
        """Retrieve all users"""
        query = "SELECT * FROM users"
        return self.db.query(query)
    
    def get_user(self, user_id):
        """Retrieve specific user"""
        query = "SELECT * FROM users WHERE id = ?"
        return self.db.queryOne(query, [user_id])
    
    def create_user(self, name, email):
        """Create user"""
        query = "INSERT INTO users (name, email) VALUES (?, ?)"
        return self.db.execute(query, [name, email])
    
    def update_user(self, user_id, data):
        """Update user"""
        query = "UPDATE users SET name = ?, email = ? WHERE id = ?"
        return self.db.execute(query, [data['name'], data['email'], user_id])
    
    def delete_user(self, user_id):
        """Delete user"""
        query = "DELETE FROM users WHERE id = ?"
        return self.db.execute(query, [user_id])
```

### 2. Using Model

**In api.py or controller.py:**

```python
# Load model
user_model = wiz.model("user").use()

# Retrieve users
users = user_model.get_users()
wiz.response.status(200, users)

# Create user
user_id = user_model.create_user("Alice", "alice@example.com")
wiz.response.status(201, {"id": user_id})
```

### 3. Filesystem-based Model

Model that manages data with files instead of database:

**project/main/src/model/storage.py**
```python
import season
import json

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.fs = wiz.project.fs("data", "storage")
    
    def save(self, key, data):
        """Save data"""
        filename = f"{key}.json"
        json_data = json.dumps(data, default=season.util.string.json_default)
        self.fs.write(filename, json_data)
    
    def load(self, key):
        """Load data"""
        filename = f"{key}.json"
        if not self.fs.exists(filename):
            return None
        return self.fs.read.json(filename)
    
    def delete(self, key):
        """Delete data"""
        filename = f"{key}.json"
        self.fs.delete(filename)
    
    def list(self):
        """Retrieve all keys"""
        files = self.fs.files()
        return [f.replace(".json", "") for f in files]
```

---

## Using Portals

Portals are reusable module packages.

### 1. Portal Structure

```
src/portal/myportal/
├── portal.json          # Portal metadata
├── app/                 # Angular components
│   └── widget.button/
├── controller/          # Controllers
│   └── base.py
├── model/               # Models
│   └── user.py
├── route/               # Routes
│   └── api/
└── libs/                # Shared libraries
    └── service.ts
```

### 2. portal.json Configuration

**src/portal/myportal/portal.json**
```json
{
    "package": "myportal",
    "title": "My Portal",
    "version": "1.0.0",
    "use_app": true,
    "use_widget": true,
    "use_route": true,
    "use_libs": true,
    "use_controller": true,
    "use_model": true,
    "use_styles": true,
    "use_assets": true
}
```

### 3. Using Portal

**Using model:**
```python
# Load portal/myportal/model/user.py
user_model = wiz.model("portal/myportal/user").use()
```

**Using component:**
```pug
// Use portal/myportal/app/widget.button
wiz-myportal-widget-button([label]="'Click'")
```

**Using library (TypeScript):**
```typescript
import { Service } from '@wiz/libs/portal/myportal/service';

constructor(public myService: Service) { }
```

### 4. Sharing Portal

Portals can be reused in other projects as independent packages.

1. Copy `src/portal/myportal` directory
2. Paste to `src/portal/` in another project
3. Automatically recognized when built

---

## Build and Deployment

### 1. Building Project

```bash
# Build from IDE (recommended)
# Access http://127.0.0.1:3000/wiz and click build button

# Build from CLI
wiz command workspace build main
```

Build output:
- `project/main/build/` - Built files
- `project/main/bundle/` - Final bundle

### 2. Running in Bundle Mode

Bundle mode uses built code for improved performance.

```bash
wiz run --bundle=true
```

### 3. Production Deployment

#### WSGI Server (Gunicorn)

```bash
# Install Gunicorn
pip install gunicorn

# Run
cd /path/to/myapp/public
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

#### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:3000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### Docker Deployment

**Dockerfile**
```dockerfile
FROM python:3.10

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# Install WIZ
RUN pip install season

# Copy project
COPY . /app
WORKDIR /app

# Expose port
EXPOSE 3000

# Run server
CMD ["wiz", "run", "--port=3000", "--host=0.0.0.0"]
```

**Build and run:**
```bash
docker build -t myapp .
docker run -p 3000:3000 myapp
```

### 4. IDE Upgrade

```bash
# Upgrade WIZ package
pip install season --upgrade

# Upgrade IDE
wiz ide upgrade
```

### 5. Environment Variable Configuration

**In config/boot.py:**
```python
import os

# Configuration by environment
ENV = os.getenv("WIZ_ENV", "development")

if ENV == "production":
    run['debug'] = False
    run['use_reloader'] = False
    secret_key = os.getenv("SECRET_KEY", "production-secret-key")
else:
    run['debug'] = True
    run['use_reloader'] = True
    secret_key = "development-secret-key"
```

---

## Additional Tips

### 1. Debugging

**Python logging:**
```python
import season

logger = season.util.Logger("myapp", level=season.LOG_DEBUG)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

**JavaScript console:**
```typescript
console.log("Debug message");
console.error("Error message");
```

### 2. Hot Reload

In development mode, automatically rebuilds on file changes.

```bash
wiz run --port=3000
```

### 3. Multi-project

You can manage multiple projects in one WIZ instance.

```
project/
├── main/        # Main application
├── admin/       # Admin page
└── api/         # API only
```

Each project is built independently and separated by URL namespace.

### 4. Plugin Development

You can extend WIZ by developing custom plugins.

```
plugin/
└── myplugin/
    ├── plugin.json
    ├── command.py
    ├── filter.py
    ├── app/
    └── model/
```

---

## References

- [Architecture Documentation](architecture.md)
- [GitHub Repository](https://github.com/season-framework/wiz)
- Official Website (coming soon)

---

## Troubleshooting

### Q: Build fails.
A: Verify that Node.js and Angular CLI are installed correctly.

### Q: Port already in use.
A: Specify a different port or terminate the process using that port.

### Q: Cannot access IDE.
A: Check firewall settings and verify that the server is running properly.

### Q: Page returns 404 error.
A: Verify that the `viewuri` setting in `app.json` is correct and rebuild.
