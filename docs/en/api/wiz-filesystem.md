# Filesystem API

API for managing files and directories.

## Overview

- **Class**: `season.util.Filesystem`
- **Access**: `wiz.fs()`, `wiz.project.fs()`, `season.util.fs()`
- **Usage Location**: `api.py`, `controller.py`, `model/*.py`

---

## Creating Filesystem

### wiz.fs()

Returns the filesystem for the current component.

```python
fs = wiz.fs()
```

### wiz.project.fs()

Returns a filesystem within the project.

```python
fs = wiz.project.fs("data", "uploads")
```

### season.util.fs()

Returns a filesystem for an arbitrary path.

```python
import season
fs = season.util.fs("/path/to/directory")
```

---

## Reading/Writing Files

### read()

Reads a file.

#### Syntax
```python
fs.read(filename, default=None)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `filename` | str | ✅ | - | Filename |
| `default` | any | ❌ | None | Value to return when file doesn't exist |

#### Return Value

| Type | Description |
|------|-------------|
| `str` or `any` | File content or default value |

#### Examples

```python
# Read text file
content = fs.read("file.txt")

# Use default value if file doesn't exist
content = fs.read("file.txt", "")

# Handle None
content = fs.read("file.txt", None)
if content is None:
    print("File not found")
```

---

### write()

Writes to a file.

#### Syntax
```python
fs.write(filename, data, mode="w")
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `filename` | str | ✅ | - | Filename |
| `data` | str/bytes | ✅ | - | Data to save |
| `mode` | str | ❌ | "w" | Write mode ("w": text, "wb": binary) |

#### Examples

```python
# Write text
fs.write("file.txt", "Hello World")

# Write binary (file upload)
file = wiz.request.file("avatar")
fs.write("avatar.png", file.read(), mode="wb")

# Overwrite
fs.write("log.txt", "New log entry")
```

---

## JSON Processing

### read.json()

Reads a JSON file.

#### Syntax
```python
fs.read.json(filename, default={})
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `filename` | str | ✅ | - | Filename |
| `default` | any | ❌ | {} | Value to return when file doesn't exist or JSON parsing fails |

#### Return Value

| Type | Description |
|------|-------------|
| `dict`/`list` or `any` | JSON data or default value |

#### Examples

```python
# Read JSON
config = fs.read.json("config.json")
print(config)  # {"key": "value"}

# Set default value
config = fs.read.json("config.json", {"theme": "light"})

# List JSON
users = fs.read.json("users.json", [])
```

---

### write.json()

Writes to a JSON file.

#### Syntax
```python
fs.write.json(filename, data)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `filename` | str | ✅ | - | Filename |
| `data` | dict/list | ✅ | - | Data to save as JSON |

#### Examples

```python
# Save dictionary
config = {"theme": "dark", "language": "ko"}
fs.write.json("config.json", config)

# Save list
users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
fs.write.json("users.json", users)
```

---

## Checking Files/Directories

### exists()

Checks if a file or directory exists.

#### Syntax
```python
fs.exists(path)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | str | ✅ | - | Path |

#### Return Value

| Type | Description |
|------|-------------|
| `bool` | True if exists, False otherwise |

#### Examples

```python
if fs.exists("config.json"):
    config = fs.read.json("config.json")

if not fs.exists("uploads"):
    fs.makedirs("uploads")
```

---

### isdir()

Checks if it's a directory.

#### Syntax
```python
fs.isdir(path)
```

#### Return Value

| Type | Description |
|------|-------------|
| `bool` | True if directory, False otherwise |

#### Examples

```python
if fs.isdir("uploads"):
    print("uploads is a directory")
```

---

## File Listing

### files()

Returns a list of files.

#### Syntax
```python
fs.files(path="")
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | str | ❌ | "" | Subdirectory path |

#### Return Value

| Type | Description |
|------|-------------|
| `list` | List of filenames (excluding directories) |

#### Examples

```python
# Files in current directory
files = fs.files()
print(files)  # ["file1.txt", "file2.json"]

# Files in subdirectory
files = fs.files("uploads")

# Process all files
for filename in fs.files():
    content = fs.read(filename)
    print(f"{filename}: {len(content)} bytes")
```

---

### ls()

Returns a list of files and directories.

#### Syntax
```python
fs.ls(path="")
```

#### Return Value

| Type | Description |
|------|-------------|
| `list` | List of filenames and directory names |

#### Examples

```python
items = fs.ls()
print(items)  # ["file.txt", "subdir", "data.json"]
```

---

## Directory Management

### makedirs()

Creates a directory (including intermediate directories).

#### Syntax
```python
fs.makedirs(path)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | str | ✅ | - | Directory path |

#### Examples

```python
# Create directory
fs.makedirs("uploads/images")
fs.makedirs("data/cache/temp")

# Create after checking existence
if not fs.exists("logs"):
    fs.makedirs("logs")
```

---

## Deleting Files/Directories

### delete()

Deletes a file or directory.

#### Syntax
```python
fs.delete(path)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | str | ✅ | - | Path to delete |

#### Examples

```python
# Delete file
fs.delete("temp.txt")

# Delete directory (including sub-items)
fs.delete("temp_folder")

# Delete after checking existence
if fs.exists("old_data.json"):
    fs.delete("old_data.json")
```

---

## Copying/Moving Files

### copy()

Copies a file or directory.

#### Syntax
```python
fs.copy(src, dst)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `src` | str | ✅ | - | Source path |
| `dst` | str | ✅ | - | Destination path |

#### Examples

```python
# Copy file
fs.copy("file.txt", "file_backup.txt")

# Copy directory
fs.copy("source_dir", "backup_dir")
```

---

### move()

Moves a file or directory.

#### Syntax
```python
fs.move(src, dst)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `src` | str | ✅ | - | Source path |
| `dst` | str | ✅ | - | Destination path |

#### Examples

```python
# Move file
fs.move("old.txt", "new.txt")

# Move directory
fs.move("old_folder", "new_folder")
```

---

## File Information

### size()

Returns the file size.

#### Syntax
```python
fs.size(filename)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `filename` | str | ✅ | - | Filename |

#### Return Value

| Type | Description |
|------|-------------|
| `int` | File size (bytes) |

#### Examples

```python
size = fs.size("file.txt")
print(f"{size} bytes")

# File list with sizes
for filename in fs.files():
    size = fs.size(filename)
    print(f"{filename}: {size} bytes")
```

---

### abspath()

Returns the absolute path.

#### Syntax
```python
fs.abspath(path="")
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | str | ❌ | "" | Relative path |

#### Return Value

| Type | Description |
|------|-------------|
| `str` | Absolute path |

#### Examples

```python
# Current directory absolute path
path = fs.abspath()
print(path)  # "/path/to/project/data"

# File absolute path
filepath = fs.abspath("file.txt")
print(filepath)  # "/path/to/project/data/file.txt"

# Use in download
filepath = fs.abspath("report.pdf")
wiz.response.download(filepath)
```

---

## Complete Examples

### File Upload Management

```python
# app/page.upload/api.py

def upload():
    """File upload"""
    fs = wiz.project.fs("data", "uploads")
    
    # Create uploads directory
    if not fs.exists(""):
        fs.makedirs("")
    
    files = wiz.request.files()
    uploaded = []
    
    for file in files:
        filename = file.filename
        
        # Save file
        fs.write(filename, file.read(), mode="wb")
        
        uploaded.append({
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
    
    if not fs.exists(""):
        wiz.response.status(200, [])
        return
    
    files = []
    for filename in fs.files():
        files.append({
            "name": filename,
            "size": fs.size(filename)
        })
    
    wiz.response.status(200, files)

def delete_file():
    """Delete file"""
    filename = wiz.request.query("filename")
    fs = wiz.project.fs("data", "uploads")
    
    if fs.exists(filename):
        fs.delete(filename)
        wiz.response.status(200, {"message": "Deleted"})
    else:
        wiz.response.status(404, {"error": "File not found"})
```

### Configuration File Management

```python
# model/config.py

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.fs = wiz.project.fs("config")
    
    def load(self, name="app"):
        """Load configuration"""
        filename = f"{name}.json"
        return self.fs.read.json(filename, {})
    
    def save(self, name, data):
        """Save configuration"""
        filename = f"{name}.json"
        self.fs.write.json(filename, data)
    
    def delete(self, name):
        """Delete configuration"""
        filename = f"{name}.json"
        if self.fs.exists(filename):
            self.fs.delete(filename)
```

### Log File Management

```python
# model/logger.py

import datetime

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.fs = wiz.project.fs("logs")
        
        # Create logs directory
        if not self.fs.exists(""):
            self.fs.makedirs("")
    
    def log(self, level, message):
        """Write log"""
        today = datetime.date.today().strftime("%Y-%m-%d")
        filename = f"{today}.log"
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Read existing content
        content = self.fs.read(filename, "")
        
        # Add new log
        content += log_entry
        
        # Save
        self.fs.write(filename, content)
    
    def get_logs(self, date=None):
        """Get logs"""
        if date is None:
            date = datetime.date.today().strftime("%Y-%m-%d")
        
        filename = f"{date}.log"
        return self.fs.read(filename, "")
```

---

## References

- [wiz.project API](wiz-project.md)
- [wiz Object API](wiz-object.md)
- [Full API List](README.md)
