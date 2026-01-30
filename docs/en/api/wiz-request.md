# wiz.request API

API for handling HTTP requests. Available in `api.py`, `controller.py`, `socket.py`, etc.

## Class Information

- **Class**: `season.lib.core.struct.Request`
- **Access**: `wiz.request`
- **Source**: `/mnt/data/git/wiz/src/season/lib/core/struct/request.py`

---

## Methods

### wiz.request.query()

Gets GET/POST parameters.

#### Syntax
```python
wiz.request.query(key=None, default=None)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `key` | str | ❌ | None | Parameter key to retrieve. If None, returns all parameters |
| `default` | any | ❌ | None | Default value when key doesn't exist. If True, raises 400 error |

#### Return Value

| Type | Description |
|------|-------------|
| `dict` | When key is None, returns all parameters as a dictionary |
| `any` | When key is specified, returns the value (or default if not found) |

#### Examples

```python
# Get all parameters
data = wiz.request.query()
# {'name': 'Alice', 'age': '25', 'email': 'alice@example.com'}

# Get specific parameter
name = wiz.request.query("name")  # "Alice"
age = wiz.request.query("age")    # "25"

# Set default value
city = wiz.request.query("city", "Seoul")  # "Seoul" (if city parameter doesn't exist)

# Required parameter (raises 400 error if missing)
email = wiz.request.query("email", True)
```

---

### wiz.request.files()

Gets the list of uploaded files.

#### Syntax
```python
wiz.request.files(namespace='file')
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `namespace` | str | ❌ | 'file' | Name attribute of file input ([] automatically added) |

#### Return Value

| Type | Description |
|------|-------------|
| `list` | List of FileStorage objects |

#### Examples

```python
# Process file uploads
files = wiz.request.files()

for file in files:
    filename = file.filename
    content = file.read()
    
    # Save file
    fs = wiz.project.fs("data", "uploads")
    fs.write(filename, content, mode="wb")

# HTML form example:
# <input type="file" name="file[]" multiple>
```

---

### wiz.request.file()

Gets a single file.

#### Syntax
```python
wiz.request.file(namespace='file')
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `namespace` | str | ❌ | 'file' | Name attribute of file input |

#### Return Value

| Type | Description |
|------|-------------|
| `FileStorage` or `None` | Uploaded file object or None |

#### Examples

```python
# Single file upload
file = wiz.request.file('avatar')

if file:
    filename = file.filename
    fs = wiz.project.fs("data", "avatars")
    fs.write(filename, file.read(), mode="wb")

# HTML form example:
# <input type="file" name="avatar">
```

---

### wiz.request.match()

Matches URL pattern and extracts segments.

#### Syntax
```python
wiz.request.match(pattern)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pattern` | str | ✅ | - | URL pattern (Werkzeug routing rule) |

#### Supported Pattern Types

| Pattern | Description | Example |
|---------|-------------|---------|
| `<name>` | String (default) | `/users/<username>` |
| `<int:name>` | Integer | `/posts/<int:id>` |
| `<float:name>` | Float | `/price/<float:amount>` |
| `<path:name>` | Path (includes /) | `/files/<path:filepath>` |

#### Return Value

| Type | Description |
|------|-------------|
| `stdClass` or `None` | Matched segment object or None |

#### Examples

```python
# URL: /api/users/123/posts/456

# Basic matching
segment = wiz.request.match("/api/<resource>/<int:id>/<sub>/<int:sub_id>")
print(segment.resource)  # "users"
print(segment.id)        # 123
print(segment.sub)       # "posts"
print(segment.sub_id)    # 456

# Path matching
# URL: /files/images/profile/avatar.png
segment = wiz.request.match("/files/<path:filepath>")
print(segment.filepath)  # "images/profile/avatar.png"

# Conditional processing
segment = wiz.request.match("/brand/<action>/<path:path>")
action = segment.action

if action == "logo":
    # Process logo
    pass
elif action == "icon":
    # Process icon
    pass
```

---

### wiz.request.uri()

Returns the URI of the current request.

#### Syntax
```python
wiz.request.uri()
```

#### Parameters

None

#### Return Value

| Type | Description |
|------|-------------|
| `str` | Request URI excluding base URL |

#### Examples

```python
# Request URL: http://localhost:3000/api/users/123
uri = wiz.request.uri()
print(uri)  # "/api/users/123"

# Use in redirect
wiz.response.redirect(wiz.request.uri())
```

---

### wiz.request.method()

Returns the HTTP method.

#### Syntax
```python
wiz.request.method()
```

#### Parameters

None

#### Return Value

| Type | Description |
|------|-------------|
| `str` | HTTP method (GET, POST, PUT, DELETE, etc.) |

#### Examples

```python
method = wiz.request.method()

if method == "GET":
    # Handle GET request
    pass
elif method == "POST":
    # Handle POST request
    pass
elif method == "PUT":
    # Handle PUT request
    pass
elif method == "DELETE":
    # Handle DELETE request
    pass
```

---

### wiz.request.headers()

Gets HTTP header values.

#### Syntax
```python
wiz.request.headers(key, default=None)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `key` | str | ✅ | - | Header name |
| `default` | any | ❌ | None | Default value when header doesn't exist |

#### Return Value

| Type | Description |
|------|-------------|
| `str` or `any` | Header value or default value |

#### Examples

```python
# Get User-Agent
user_agent = wiz.request.headers("User-Agent")
print(user_agent)  # "Mozilla/5.0 ..."

# Authorization header
auth = wiz.request.headers("Authorization", "")
if auth.startswith("Bearer "):
    token = auth[7:]  # Remove "Bearer "

# Content-Type
content_type = wiz.request.headers("Content-Type", "application/json")
```

---

### wiz.request.cookies()

Gets cookie values.

#### Syntax
```python
wiz.request.cookies(key, default=None)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `key` | str | ✅ | - | Cookie name |
| `default` | any | ❌ | None | Default value when cookie doesn't exist |

#### Return Value

| Type | Description |
|------|-------------|
| `str` or `any` | Cookie value or default value |

#### Examples

```python
# Get session ID
session_id = wiz.request.cookies("session_id")

# Language setting
lang = wiz.request.cookies("language", "ko")

# Project selection
project = wiz.request.cookies("season-wiz-project", "main")
```

---

### wiz.request.ip()

Gets the client IP address.

#### Syntax
```python
wiz.request.ip()
```

#### Parameters

None

#### Return Value

| Type | Description |
|------|-------------|
| `str` | Client IP address |

#### Examples

```python
ip = wiz.request.ip()
print(ip)  # "192.168.1.100"

# Logging
logger = wiz.logger("access")
logger.info(f"Request from {ip}")

# IP-based access control
allowed_ips = ["127.0.0.1", "192.168.1.0/24"]
if ip not in allowed_ips:
    wiz.response.abort(403)
```

---

### wiz.request.language()

Gets the request language.

#### Syntax
```python
wiz.request.language()
```

#### Parameters

None

#### Return Value

| Type | Description |
|------|-------------|
| `str` | Language code (uppercase, e.g., "KO", "EN", "DEFAULT") |

#### Examples

```python
lang = wiz.request.language()
print(lang)  # "KO"

# Language-specific processing
if lang == "KO":
    message = "안녕하세요"
elif lang == "EN":
    message = "Hello"
else:
    message = "Hello"

wiz.response.status(200, {"message": message})
```

---

### wiz.request.request()

Direct access to the Flask request object.

#### Syntax
```python
wiz.request.request()
```

#### Parameters

None

#### Return Value

| Type | Description |
|------|-------------|
| `flask.Request` | Flask request object |

#### Examples

```python
req = wiz.request.request()

# Full URL
print(req.url)  # "http://localhost:3000/api/users?page=1"

# Base URL
print(req.base_url)  # "http://localhost:3000/api/users"

# Method
print(req.method)  # "GET"

# All headers
headers = dict(req.headers)

# Form data
form_data = dict(req.form)

# JSON data
json_data = req.get_json()

# Remote address
print(req.remote_addr)  # "127.0.0.1"
```

---

## Complete Examples

### RESTful API Endpoint

```python
# route/api/controller.py

# URL matching
segment = wiz.request.match("/api/<resource>/<path:path>")
resource = segment.resource
path = segment.path

# HTTP method
method = wiz.request.method()

# Database
db = wiz.model("database").use()

if resource == "users":
    if method == "GET":
        if path:
            # GET /api/users/123
            user_id = path
            user = db.get_user(user_id)
            wiz.response.status(200, user)
        else:
            # GET /api/users
            users = db.get_users()
            wiz.response.status(200, users)
    
    elif method == "POST":
        # POST /api/users
        data = wiz.request.query()
        user_id = db.create_user(data)
        wiz.response.status(201, {"id": user_id})
    
    elif method == "PUT":
        # PUT /api/users/123
        user_id = path
        data = wiz.request.query()
        db.update_user(user_id, data)
        wiz.response.status(200, {"result": "success"})
    
    elif method == "DELETE":
        # DELETE /api/users/123
        user_id = path
        db.delete_user(user_id)
        wiz.response.status(204)

wiz.response.abort(404)
```

### File Upload Processing

```python
# app/page.upload/api.py

def upload():
    """File upload"""
    files = wiz.request.files()
    
    if len(files) == 0:
        wiz.response.status(400, {"error": "No files uploaded"})
        return
    
    fs = wiz.project.fs("data", "uploads")
    uploaded = []
    
    for file in files:
        filename = file.filename
        fs.write(filename, file.read(), mode="wb")
        uploaded.append({
            "name": filename,
            "size": fs.size(filename)
        })
    
    wiz.response.status(200, {
        "files": uploaded,
        "count": len(uploaded)
    })
```

### Authentication Processing

```python
# controller/base.py

class Controller:
    def __init__(self):
        # Token authentication
        auth = wiz.request.headers("Authorization", "")
        
        if auth.startswith("Bearer "):
            token = auth[7:]
            auth_model = wiz.model("auth").use()
            user_id = auth_model.verify_token(token)
            
            if user_id:
                wiz.session.set("user_id", user_id)
            else:
                wiz.response.status(401, {"error": "Invalid token"})
        
        # IP-based restriction
        ip = wiz.request.ip()
        if ip in blacklist:
            wiz.response.abort(403)
```

---

## References

- [wiz.response API](wiz-response.md)
- [wiz.session API](wiz-session.md)
- [Full API List](README.md)
