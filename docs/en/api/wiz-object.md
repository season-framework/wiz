# wiz Object API

The core object of the WIZ framework, serving as the entry point for all APIs available in Python code.

## Class Information

- **Class**: `season.lib.core.Wiz`
- **Access**: `wiz` (global object)
- **Source**: `/mnt/data/git/wiz/src/season/lib/core/wiz.py`
- **Usage Location**: `api.py`, `controller.py`, `socket.py`, `model/*.py`, `route/*/controller.py`

---

## Sub-API Objects

### wiz.request

API for handling HTTP requests.

| Method | Description | Documentation |
|--------|-------------|--------------|
| `wiz.request.query()` | Get GET/POST parameters | [Details](wiz-request.md#wizrequestquery) |
| `wiz.request.files()` | Get uploaded files list | [Details](wiz-request.md#wizrequestfiles) |
| `wiz.request.file()` | Get single file | [Details](wiz-request.md#wizrequestfile) |
| `wiz.request.match()` | URL pattern matching | [Details](wiz-request.md#wizrequestmatch) |
| `wiz.request.uri()` | Current request URI | [Details](wiz-request.md#wizrequesturi) |
| `wiz.request.method()` | HTTP method | [Details](wiz-request.md#wizrequestmethod) |
| `wiz.request.headers()` | HTTP headers | [Details](wiz-request.md#wizrequestheaders) |
| `wiz.request.cookies()` | Cookie values | [Details](wiz-request.md#wizrequestcookies) |
| `wiz.request.ip()` | Client IP | [Details](wiz-request.md#wizrequestip) |

📖 **Full Documentation**: [wiz.request API](wiz-request.md)

---

### wiz.response

API for generating HTTP responses.

| Method | Description | Documentation |
|--------|-------------|--------------|
| `wiz.response.status()` | JSON response | [Details](wiz-response.md#wizresponsestatus) |
| `wiz.response.download()` | File download | [Details](wiz-response.md#wizresponsedownload) |
| `wiz.response.redirect()` | URL redirect | [Details](wiz-response.md#wizresponseredirect) |
| `wiz.response.abort()` | Raise HTTP error | [Details](wiz-response.md#wizresponseabort) |
| `wiz.response.send()` | Text response | [Details](wiz-response.md#wizresponsesend) |
| `wiz.response.json()` | JSON response | [Details](wiz-response.md#wizresponsejson) |
| `wiz.response.PIL()` | Image response | [Details](wiz-response.md#wizresponsepil) |
| `wiz.response.stream()` | Streaming | [Details](wiz-response.md#wizresponsestream) |

📖 **Full Documentation**: [wiz.response API](wiz-response.md)

---

### wiz.project

API for project management and filesystem access.

| Method | Description | Documentation |
|--------|-------------|--------------|
| `wiz.project()` | Current project name | [Details](wiz-project.md#wizproject) |
| `wiz.project.checkout()` | Checkout project | [Details](wiz-project.md#wizprojectcheckout) |
| `wiz.project.exists()` | Check project existence | [Details](wiz-project.md#wizprojectexists) |
| `wiz.project.list()` | Project list | [Details](wiz-project.md#wizprojectlist) |
| `wiz.project.path()` | Project path | [Details](wiz-project.md#wizprojectpath) |
| `wiz.project.fs()` | Filesystem object | [Details](wiz-project.md#wizprojectfs) |
| `wiz.project.dev()` | Development mode | [Details](wiz-project.md#wizprojectdev) |

📖 **Full Documentation**: [wiz.project API](wiz-project.md)

---

### wiz.session

API for session management.

| Method | Description |
|--------|-------------|
| `wiz.session.set(key, value)` | Set session value |
| `wiz.session.get(key, default)` | Get session value |
| `wiz.session.delete(key)` | Delete session value |
| `wiz.session.clear()` | Clear all sessions |

📖 **Full Documentation**: [wiz.session API](wiz-session.md)

---

## Methods

### wiz.fs()

Returns a filesystem object for the current location.

#### Syntax
```python
wiz.fs(*args)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `*args` | str | ❌ | - | Path segments |

#### Return Value

| Type | Description |
|------|-------------|
| `Filesystem` | Filesystem object |

#### Examples

```python
# Current component directory
fs = wiz.fs()
content = fs.read("data.json")

# Subdirectory
fs = wiz.fs("config")
config = fs.read.json("settings.json")
```

---

### wiz.path()

Returns the WIZ root path.

#### Syntax
```python
wiz.path(*args)
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
# WIZ root path
root = wiz.path()
print(root)  # "/path/to/wiz"

# config path
config_path = wiz.path("config")
print(config_path)  # "/path/to/wiz/config"
```

---

### wiz.model()

Loads a model.

#### Syntax
```python
wiz.model(namespace)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `namespace` | str | ✅ | - | Model namespace |

#### Return Value

| Type | Description |
|------|-------------|
| `class` | Model class |

#### Examples

```python
# Project model
UserModel = wiz.model("user")
user_instance = UserModel(wiz)

# Using use() helper
user_model = wiz.model("user").use()
users = user_model.get_all()

# Portal model
session_model = wiz.model("portal/season/session").use()
sessiondata = session_model.get()
```

---

### wiz.controller()

Loads a controller.

#### Syntax
```python
wiz.controller(namespace)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `namespace` | str | ✅ | - | Controller namespace |

#### Return Value

| Type | Description |
|------|-------------|
| `class` | Controller class |

#### Examples

```python
# Load base controller
BaseController = wiz.controller("base")
base = BaseController()
```

---

### wiz.logger()

Creates a logger object.

#### Syntax
```python
wiz.logger(*tags)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `*tags` | str | ❌ | - | Log tags |

#### Return Value

| Type | Description |
|------|-------------|
| `Logger` | Logger object |

#### Logger Methods

| Method | Description |
|--------|-------------|
| `debug(message)` | Debug log |
| `info(message)` | Info log |
| `warning(message)` | Warning log |
| `error(message)` | Error log |
| `critical(message)` | Critical error log |

#### Examples

```python
# Create logger
logger = wiz.logger("myapp", "api")

# Log output
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")

# Logs with timestamp (automatic)
# [125ms] [myapp] [api] Info message
```

---

### wiz.src()

Returns the project's bundle/src path filesystem.

#### Syntax
```python
wiz.src(*args)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `*args` | str | ❌ | - | Path segments |

#### Return Value

| Type | Description |
|------|-------------|
| `Filesystem` | Filesystem object |

#### Examples

```python
# src filesystem
fs = wiz.src()

# app directory
fs = wiz.src("app")

# model directory
fs = wiz.src("model")
```

---

## Complete Usage Examples

### API Handler

```python
# app/page.users/api.py

def get_users():
    """Get user list"""
    # Logger
    logger = wiz.logger("users", "api")
    logger.info("Get users request")
    
    # Load model
    user_model = wiz.model("user").use()
    users = user_model.get_all()
    
    # Response
    wiz.response.status(200, users)

def create_user():
    """Create user"""
    # Request data
    data = wiz.request.query()
    
    # Validation
    if not data.get("email"):
        wiz.response.status(400, {"error": "Email required"})
        return
    
    # Use model
    user_model = wiz.model("user").use()
    user_id = user_model.create(data)
    
    # Set session
    wiz.session.set("last_created_user", user_id)
    
    # Response
    wiz.response.status(201, {"id": user_id})

def upload_avatar():
    """Upload avatar"""
    # Get file
    file = wiz.request.file("avatar")
    
    if not file:
        wiz.response.status(400, {"error": "No file"})
        return
    
    # Save file
    fs = wiz.project.fs("data", "avatars")
    filename = file.filename
    fs.write(filename, file.read(), mode="wb")
    
    # Response
    wiz.response.status(200, {
        "filename": filename,
        "path": fs.abspath(filename)
    })
```

### Controller

```python
# controller/base.py

class Controller:
    def __init__(self):
        # Current project
        project = wiz.project()
        
        # Session model
        session_model = wiz.model("portal/season/session").use()
        sessiondata = session_model.get()
        
        # Pass data to template
        wiz.response.data.set(
            project=project,
            session=sessiondata
        )
        
        # Check authentication
        user_id = wiz.session.get("user_id")
        if not user_id:
            # Check protected pages
            uri = wiz.request.uri()
            protected = ["/dashboard", "/admin"]
            
            if any(uri.startswith(p) for p in protected):
                wiz.response.redirect("/login")
```

### Route

```python
# route/api/controller.py

# URL matching
segment = wiz.request.match("/api/<resource>/<path:path>")
resource = segment.resource
path = segment.path

# HTTP method
method = wiz.request.method()

# Logger
logger = wiz.logger("api", resource)
logger.info(f"{method} /{resource}/{path}")

# Model
db = wiz.model("database").use()

if resource == "users":
    if method == "GET":
        users = db.query("SELECT * FROM users")
        wiz.response.status(200, users)
    elif method == "POST":
        data = wiz.request.query()
        user_id = db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            [data.get("name"), data.get("email")]
        )
        wiz.response.status(201, {"id": user_id})

wiz.response.abort(404)
```

---

## References

- [wiz.request API](wiz-request.md)
- [wiz.response API](wiz-response.md)
- [wiz.project API](wiz-project.md)
- [wiz.session API](wiz-session.md)
- [Service API (TypeScript)](service-api.md)
- [Full API List](README.md)
