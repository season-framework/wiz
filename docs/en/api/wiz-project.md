# wiz.project API

API for project management and filesystem access.

## Class Information

- **Class**: `season.lib.core.struct.Project`
- **Access**: `wiz.project`
- **Source**: `/mnt/data/git/wiz/src/season/lib/core/struct/project.py`

---

## Methods

### wiz.project()

Returns the current project name or checks out a project.

#### Syntax
```python
# Get current project
project_name = wiz.project()

# Checkout project
wiz.project(project)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project` | str | ❌ | None | Project name to checkout. If None, returns current project |

#### Return Value

| Type | Description |
|------|-------------|
| `str` | Project name (e.g., "main") |

#### Examples

```python
# Check current project
current = wiz.project()
print(current)  # "main"

# Checkout project
wiz.project("admin")
print(wiz.project())  # "admin"

# Project-specific processing
project = wiz.project()
if project == "main":
    # Main project logic
    pass
elif project == "admin":
    # Admin project logic
    pass
```

---

### wiz.project.checkout()

Checks out a project.

#### Syntax
```python
wiz.project.checkout(project)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project` | str | ✅ | - | Project name to checkout |

#### Return Value

| Type | Description |
|------|-------------|
| `str` | Checked out project name |

#### Behavior

- If project exists, saves it in cookie and sets it as current project
- If project doesn't exist, maintains current project

#### Examples

```python
# Checkout project
wiz.project.checkout("main")

# Non-existent project is ignored
wiz.project.checkout("nonexistent")  # Current project maintained

# Use in CLI command
def build(*args):
    project = args[0]
    wiz.project.checkout(project)
    builder = wiz.ide.plugin.model("builder")
    builder.build()
```

---

### wiz.project.exists()

Checks if a project exists.

#### Syntax
```python
wiz.project.exists(project)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project` | str | ✅ | - | Project name to check |

#### Return Value

| Type | Description |
|------|-------------|
| `bool` | True if project exists, False otherwise |

#### Examples

```python
# Check project existence
if wiz.project.exists("admin"):
    print("Admin project exists")

# Check before project creation
project_name = "new_project"
if not wiz.project.exists(project_name):
    # Project creation logic
    pass
else:
    wiz.response.status(400, {"error": "Project already exists"})
```

---

### wiz.project.list()

Returns a list of all projects.

#### Syntax
```python
wiz.project.list()
```

#### Parameters

None

#### Return Value

| Type | Description |
|------|-------------|
| `list` | List of project names |

#### Examples

```python
# Get project list
projects = wiz.project.list()
print(projects)  # ["main", "admin", "api"]

# API response
def get_projects():
    projects = wiz.project.list()
    wiz.response.status(200, projects)
```

---

### wiz.project.path()

Returns a path within the project.

#### Syntax
```python
wiz.project.path(*args)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `*args` | str | ❌ | - | Path segments |

#### Return Value

| Type | Description |
|------|-------------|
| `str` | Absolute path |

#### Examples

```python
# Project root path
root = wiz.project.path()
print(root)  # "/path/to/project/main"

# Subdirectory path
data_path = wiz.project.path("data")
print(data_path)  # "/path/to/project/main/data"

# Deep path
uploads_path = wiz.project.path("data", "uploads", "images")
print(uploads_path)  # "/path/to/project/main/data/uploads/images"
```

---

### wiz.project.fs()

Returns a filesystem object within the project.

#### Syntax
```python
wiz.project.fs(*args)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `*args` | str | ❌ | - | Path segments |

#### Return Value

| Type | Description |
|------|-------------|
| `Filesystem` | Filesystem object |

#### Filesystem Methods

| Method | Description |
|--------|-------------|
| `read(filename)` | Read file |
| `write(filename, data, mode="w")` | Write file |
| `read.json(filename, default={})` | Read JSON |
| `write.json(filename, data)` | Write JSON |
| `exists(filename)` | Check file/directory existence |
| `isdir(path)` | Check if directory |
| `delete(path)` | Delete file/directory |
| `makedirs(path)` | Create directory |
| `files(path="")` | File list |
| `ls(path="")` | File/directory list |
| `size(filename)` | File size |
| `abspath(filename)` | Absolute path |
| `copy(src, dst)` | Copy |
| `move(src, dst)` | Move |

#### Examples

```python
# Data directory filesystem
fs = wiz.project.fs("data")

# Read file
content = fs.read("file.txt")

# Write file
fs.write("file.txt", "Hello World")

# Read/write JSON
data = fs.read.json("config.json", default={})
fs.write.json("config.json", {"key": "value"})

# Check file existence
if fs.exists("users.db"):
    # Use database
    pass

# Create directory
fs.makedirs("uploads/images")

# File list
files = fs.files()
for filename in files:
    print(filename)

# Get absolute path
filepath = fs.abspath("file.txt")
print(filepath)  # "/path/to/project/main/data/file.txt"

# Save uploaded file
fs_uploads = wiz.project.fs("data", "uploads")
files = wiz.request.files()
for file in files:
    fs_uploads.write(file.filename, file.read(), mode="wb")

# CSV export
fs_exports = wiz.project.fs("data", "exports")
csv_data = "name,email\nAlice,alice@example.com"
fs_exports.write("users.csv", csv_data)
filepath = fs_exports.abspath("users.csv")
wiz.response.download(filepath)
```

---

### wiz.project.dev()

Checks or sets development mode state.

#### Syntax
```python
# Check development mode
is_dev = wiz.project.dev()

# Set development mode
wiz.project.dev(True)  # Activate development mode
wiz.project.dev(False)  # Deactivate development mode
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `devmode` | bool | ❌ | None | Set development mode. If None, returns current state |

#### Return Value

| Type | Description |
|------|-------------|
| `bool` | Development mode status |

#### Examples

```python
# Check development mode
if wiz.project.dev():
    # Run only in development mode
    print("Development mode")

# Activate development mode
wiz.project.dev(True)

# Development/production branching
if wiz.project.dev():
    # Development environment settings
    debug = True
    log_level = "DEBUG"
else:
    # Production environment settings
    debug = False
    log_level = "ERROR"
```

---

## Complete Examples

### Project-specific Data Management

```python
# model/storage.py

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.fs = wiz.project.fs("data", "storage")
    
    def save(self, key, data):
        """Save data"""
        filename = f"{key}.json"
        self.fs.write.json(filename, data)
    
    def load(self, key):
        """Load data"""
        filename = f"{key}.json"
        if not self.fs.exists(filename):
            return None
        return self.fs.read.json(filename)
    
    def delete(self, key):
        """Delete data"""
        filename = f"{key}.json"
        if self.fs.exists(filename):
            self.fs.delete(filename)
    
    def list(self):
        """List all keys"""
        files = self.fs.files()
        return [f.replace(".json", "") for f in files if f.endswith(".json")]
```

### File Upload (Project-specific)

```python
# app/page.upload/api.py

def upload():
    """File upload"""
    # Current project's uploads directory
    fs = wiz.project.fs("data", "uploads")
    
    files = wiz.request.files()
    uploaded = []
    
    for file in files:
        filename = file.filename
        
        # Save file
        fs.write(filename, file.read(), mode="wb")
        
        uploaded.append({
            "project": wiz.project(),
            "name": filename,
            "size": fs.size(filename),
            "path": fs.abspath(filename)
        })
    
    wiz.response.status(200, {
        "files": uploaded,
        "count": len(uploaded)
    })

def list_files():
    """File list"""
    fs = wiz.project.fs("data", "uploads")
    
    files = []
    for filename in fs.files():
        files.append({
            "name": filename,
            "size": fs.size(filename)
        })
    
    wiz.response.status(200, files)

def download():
    """File download"""
    filename = wiz.request.query("filename")
    fs = wiz.project.fs("data", "uploads")
    
    if not fs.exists(filename):
        wiz.response.status(404, {"error": "File not found"})
    else:
        filepath = fs.abspath(filename)
        wiz.response.download(filepath)
```

### Multi-project Management

```python
# app/page.projects/api.py

def get_projects():
    """Project list"""
    projects = wiz.project.list()
    current = wiz.project()
    
    result = []
    for project in projects:
        result.append({
            "name": project,
            "current": project == current
        })
    
    wiz.response.status(200, result)

def switch_project():
    """Switch project"""
    project = wiz.request.query("project")
    
    if not wiz.project.exists(project):
        wiz.response.status(404, {"error": "Project not found"})
        return
    
    wiz.project.checkout(project)
    wiz.response.status(200, {
        "message": "Project switched",
        "project": wiz.project()
    })

def create_project():
    """Create project"""
    project = wiz.request.query("name")
    
    if wiz.project.exists(project):
        wiz.response.status(400, {"error": "Project already exists"})
        return
    
    # Create project directory
    import os
    project_path = os.path.join(wiz.server.path.project, project)
    os.makedirs(project_path)
    
    # Create basic structure
    os.makedirs(os.path.join(project_path, "src"))
    os.makedirs(os.path.join(project_path, "data"))
    
    wiz.response.status(201, {
        "message": "Project created",
        "project": project
    })
```

### Environment-specific Configuration

```python
# config/boot.py

def bootstrap(app, config):
    """Bootstrap function"""
    import os
    
    # Environment variable
    ENV = os.getenv("ENV", "development")
    
    if ENV == "production":
        # Production settings
        config.boot.run['debug'] = False
        config.boot.log_level = season.LOG_ERROR
    else:
        # Development settings
        config.boot.run['debug'] = True
        config.boot.log_level = season.LOG_DEBUG

# Project-specific settings
project = wiz.project()

if project == "main":
    # Main project settings
    run['port'] = 3000
elif project == "admin":
    # Admin project settings
    run['port'] = 3001
```

---

## References

- [wiz.fs() API](wiz-filesystem.md)
- [wiz.request API](wiz-request.md)
- [Full API List](README.md)
