# wiz.response API

API for generating HTTP responses. Available in `api.py`, `controller.py`, `socket.py`, etc.

## Class Information

- **Class**: `season.lib.core.struct.Response`
- **Access**: `wiz.response`
- **Source**: `/mnt/data/git/wiz/src/season/lib/core/struct/response.py`

---

## Methods

### wiz.response.status()

Returns a standard response in JSON format.

#### Syntax
```python
wiz.response.status(status_code, data=None, **kwargs)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status_code` | int | ✅ | - | HTTP status code |
| `data` | dict/any | ❌ | None | Response data |
| `**kwargs` | - | ❌ | - | Additional keyword arguments (when data is None) |

#### Response Format

```json
{
    "code": 200,
    "data": { ... }
}
```

#### HTTP Status Codes

| Code | Description | When to Use |
|------|-------------|-------------|
| 200 | OK | Successful request |
| 201 | Created | Resource created |
| 204 | No Content | Success (no response body) |
| 400 | Bad Request | Invalid request |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | No permission |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

#### Examples

```python
# Success response
data = {"message": "Success", "user_id": 123}
wiz.response.status(200, data)
# Response: {"code": 200, "data": {"message": "Success", "user_id": 123}}

# Created
wiz.response.status(201, {"id": 456})
# Response: {"code": 201, "data": {"id": 456}}

# Error response
wiz.response.status(404, {"error": "User not found"})
# Response: {"code": 404, "data": {"error": "User not found"}}

# Using kwargs
wiz.response.status(200, message="OK", count=10)
# Response: {"code": 200, "data": {"message": "OK", "count": 10}}

# Status code only
wiz.response.status(204)
# Response: {"code": 204}
```

---

### wiz.response.download()

Generates a file download response.

#### Syntax
```python
wiz.response.download(filepath, as_attachment=True, filename=None)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `filepath` | str | ✅ | - | Absolute path to the file to download |
| `as_attachment` | bool | ❌ | True | True: download, False: display in browser |
| `filename` | str | ❌ | None | Filename for download (None uses original filename) |

#### Examples

```python
# File download
filepath = "/path/to/file.pdf"
wiz.response.download(filepath)

# Display in browser (PDF, images, etc.)
wiz.response.download(filepath, as_attachment=False)

# Download with custom filename
wiz.response.download(filepath, filename="report_2026.pdf")

# Download project file
fs = wiz.project.fs("data", "exports")
filepath = fs.abspath("data.csv")
wiz.response.download(filepath)

# 404 if file doesn't exist
filename = wiz.request.query("filename")
fs = wiz.project.fs("data", "files")

if not fs.exists(filename):
    wiz.response.status(404, {"error": "File not found"})
else:
    filepath = fs.abspath(filename)
    wiz.response.download(filepath)
```

---

### wiz.response.redirect()

Redirects to another URL.

#### Syntax
```python
wiz.response.redirect(url)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | str | ✅ | - | URL to redirect to |

#### Examples

```python
# Redirect to absolute path
wiz.response.redirect("/dashboard")

# External URL
wiz.response.redirect("https://example.com")

# Redirect to current URI (refresh)
wiz.response.redirect(wiz.request.uri())

# Redirect after login
def login():
    data = wiz.request.query()
    # Login processing...
    
    redirect_url = wiz.request.query("redirect", "/")
    wiz.response.redirect(redirect_url)

# Redirect after language change
def change_language():
    lang = wiz.request.query("lang")
    wiz.response.lang(lang)
    wiz.response.redirect(wiz.request.uri())
```

---

### wiz.response.abort()

Raises an HTTP error.

#### Syntax
```python
wiz.response.abort(code=500)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `code` | int | ❌ | 500 | HTTP error code |

#### Examples

```python
# 404 error
if not user_exists:
    wiz.response.abort(404)

# 403 error (no permission)
if not has_permission:
    wiz.response.abort(403)

# 401 error (authentication required)
if not is_authenticated:
    wiz.response.abort(401)

# 500 error (server error)
wiz.response.abort(500)
```

---

### wiz.response.send()

Sends a text response.

#### Syntax
```python
wiz.response.send(message, content_type=None)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `message` | str | ✅ | - | Message to send |
| `content_type` | str | ❌ | None | Content-Type header |

#### Examples

```python
# Plain text
wiz.response.send("Hello World")

# HTML
html = "<h1>Hello</h1><p>Welcome</p>"
wiz.response.send(html, content_type="text/html")

# XML
xml = '<?xml version="1.0"?><root><item>data</item></root>'
wiz.response.send(xml, content_type="application/xml")

# Also used in WebSocket (socket.py)
def on_message(data):
    wiz.response.send({"echo": data})
```

---

### wiz.response.json()

Sends a JSON response.

#### Syntax
```python
wiz.response.json(obj)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `obj` | dict/any | ✅ | - | Object to convert to JSON |

#### Examples

```python
# Send dictionary
data = {"name": "Alice", "age": 25}
wiz.response.json(data)

# Send list
users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
wiz.response.json(users)

# Automatic datetime conversion
import datetime
data = {"timestamp": datetime.datetime.now()}
wiz.response.json(data)  # Automatically converted to string
```

---

### wiz.response.PIL()

Sends a PIL image as response.

#### Syntax
```python
wiz.response.PIL(pil_image, type='JPEG', mimetype='image/jpeg', as_attachment=False, filename=None)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pil_image` | PIL.Image | ✅ | - | PIL image object |
| `type` | str | ❌ | 'JPEG' | Image format (JPEG, PNG, GIF, BMP) |
| `mimetype` | str | ❌ | 'image/jpeg' | MIME type |
| `as_attachment` | bool | ❌ | False | Whether to download |
| `filename` | str | ❌ | None | Filename |

#### Examples

```python
from PIL import Image
from io import BytesIO
import base64

# Open image file
img = Image.open("/path/to/image.png")
wiz.response.PIL(img, type="PNG", mimetype="image/png")

# Resize image
img = Image.open("/path/to/image.jpg")
img = img.resize((800, 600), Image.LANCZOS)
wiz.response.PIL(img, type="JPEG")

# Create thumbnail
img = Image.open("/path/to/image.jpg")
img.thumbnail((150, 150), Image.LANCZOS)
wiz.response.PIL(img, type="JPEG")

# Base64 decoding
def load_base64_image():
    data = wiz.request.query("image")
    img_data = data.split(",")[1]  # Remove "data:image/png;base64,"
    buf = BytesIO(base64.b64decode(img_data))
    img = Image.open(buf)
    
    # Process...
    img = img.convert('RGB')
    wiz.response.PIL(img, type="PNG")
```

---

### wiz.response.stream()

Generates a video/audio streaming response.

#### Syntax
```python
wiz.response.stream(filepath, rangeHeader=None, mimetype='video/mp4', content_type=None, direct_passthrough=True)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `filepath` | str | ✅ | - | Path to file for streaming |
| `rangeHeader` | str | ❌ | None | Range header value |
| `mimetype` | str | ❌ | 'video/mp4' | MIME type |
| `content_type` | str | ❌ | None | Content-Type (uses mimetype if None) |
| `direct_passthrough` | bool | ❌ | True | Direct transmission flag |

#### Examples

```python
# Video streaming
filepath = "/path/to/video.mp4"
range_header = wiz.request.headers("Range")
wiz.response.stream(filepath, rangeHeader=range_header)

# Audio streaming
filepath = "/path/to/audio.mp3"
range_header = wiz.request.headers("Range")
wiz.response.stream(filepath, rangeHeader=range_header, mimetype="audio/mpeg")
```

---

### wiz.response.lang() / wiz.response.language()

Sets the response language.

#### Syntax
```python
wiz.response.lang(lang)
wiz.response.language(lang)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `lang` | str | ✅ | - | Language code (2 characters) |

#### Examples

```python
# Set language
wiz.response.lang("ko")  # Korean
wiz.response.lang("en")  # English
wiz.response.lang("ja")  # Japanese

# Redirect after language change
def change_language():
    lang = wiz.request.query("lang", "ko")
    wiz.response.lang(lang)
    wiz.response.redirect(wiz.request.uri())
```

---

## Response Helper Objects

### wiz.response.data

Object for managing response data.

#### Methods

##### wiz.response.data.set()

Sets data to use in templates.

```python
wiz.response.data.set(key1=value1, key2=value2, ...)
```

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `**kwargs` | - | ✅ | Data in keyword argument form |

**Examples**

```python
# Set template variables in controller
wiz.response.data.set(username="Alice", role="admin")

# Set multiple variables
wiz.response.data.set(
    title="Dashboard",
    user={"id": 1, "name": "Alice"},
    items=[1, 2, 3, 4, 5]
)
```

##### wiz.response.data.get()

Gets the set data.

```python
wiz.response.data.get(key=None)
```

**Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `key` | str | ❌ | None | Key to retrieve. Returns all data if None |

**Examples**

```python
# All data
data = wiz.response.data.get()

# Specific key
username = wiz.response.data.get("username")
```

##### wiz.response.data.set_json()

Sets data in JSON format.

```python
wiz.response.data.set_json(key=value, ...)
```

**Examples**

```python
import datetime

# Automatically convert datetime objects to JSON strings
wiz.response.data.set_json(
    timestamp=datetime.datetime.now(),
    user={"id": 1, "name": "Alice"}
)
```

---

### wiz.response.headers

Object for managing response headers.

#### Methods

##### wiz.response.headers.set()

Sets response headers.

```python
wiz.response.headers.set(key1=value1, key2=value2, ...)
```

**Examples**

```python
# Set custom headers
wiz.response.headers.set(**{
    'X-Custom-Header': 'value',
    'Cache-Control': 'no-cache'
})

# Set Content-Type
wiz.response.headers.set(**{'Content-Type': 'text/html'})

# CORS headers
wiz.response.headers.set(**{
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE'
})
```

##### wiz.response.headers.get()

Gets set headers.

```python
wiz.response.headers.get(name=None)
```

---

### wiz.response.cookies

Object for managing response cookies.

#### Methods

##### wiz.response.cookies.set()

Sets cookies.

```python
wiz.response.cookies.set(key1=value1, key2=value2, ...)
```

**Examples**

```python
# Set cookies
wiz.response.cookies.set(**{
    'session_id': 'abc123',
    'user_pref': 'dark_mode'
})

# Language cookie
wiz.response.cookies.set(**{'framework-language': 'KO'})

# Project cookie
wiz.response.cookies.set(**{'season-wiz-project': 'main'})
```

---

## Complete Examples

### RESTful API Response

```python
# app/page.users/api.py

def get_users():
    """Get user list"""
    db = wiz.model("database").use()
    users = db.query("SELECT * FROM users")
    wiz.response.status(200, users)

def get_user():
    """Get user details"""
    user_id = wiz.request.query("id")
    db = wiz.model("database").use()
    user = db.query_one("SELECT * FROM users WHERE id = ?", [user_id])
    
    if user:
        wiz.response.status(200, user)
    else:
        wiz.response.status(404, {"error": "User not found"})

def create_user():
    """Create user"""
    data = wiz.request.query()
    name = data.get("name")
    email = data.get("email")
    
    # Validation
    if not name or not email:
        wiz.response.status(400, {"error": "Name and email required"})
        return
    
    db = wiz.model("database").use()
    user_id = db.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        [name, email]
    )
    
    wiz.response.status(201, {"id": user_id})

def delete_user():
    """Delete user"""
    user_id = wiz.request.query("id")
    db = wiz.model("database").use()
    
    db.execute("DELETE FROM users WHERE id = ?", [user_id])
    wiz.response.status(204)
```

### File Download

```python
# route/download/controller.py

segment = wiz.request.match("/download/<file_type>/<filename>")
file_type = segment.file_type
filename = segment.filename

fs = wiz.project.fs("data", file_type)

if not fs.exists(filename):
    wiz.response.status(404, {"error": "File not found"})
else:
    filepath = fs.abspath(filename)
    wiz.response.download(filepath)
```

### Image Processing

```python
# app/page.image/api.py

from PIL import Image

def thumbnail():
    """Create thumbnail"""
    filename = wiz.request.query("filename")
    size = int(wiz.request.query("size", 150))
    
    fs = wiz.project.fs("data", "images")
    
    if not fs.exists(filename):
        wiz.response.abort(404)
    
    img = Image.open(fs.abspath(filename))
    img.thumbnail((size, size), Image.LANCZOS)
    
    wiz.response.PIL(img, type="PNG", mimetype="image/png")

def resize():
    """Resize image"""
    files = wiz.request.files()
    width = int(wiz.request.query("width", 800))
    height = int(wiz.request.query("height", 600))
    
    if len(files) == 0:
        wiz.response.status(400, {"error": "No image uploaded"})
        return
    
    file = files[0]
    img = Image.open(file)
    img = img.resize((width, height), Image.LANCZOS)
    
    fs = wiz.project.fs("data", "resized")
    output = fs.abspath("resized.png")
    img.save(output)
    
    wiz.response.status(200, {"message": "Image resized", "size": [width, height]})
```

---

## References

- [wiz.request API](wiz-request.md)
- [wiz.session API](wiz-session.md)
- [Full API List](README.md)
