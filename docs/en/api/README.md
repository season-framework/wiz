# WIZ Framework API Reference

Complete API reference documentation for the WIZ framework.

## 📚 API Categories

### Backend API (Python)

#### 1. [wiz Object](wiz-object.md)
The core object of the WIZ framework, providing all APIs available in Python code (api.py, controller.py, models, etc.).

- **[wiz.request](wiz-request.md)** - HTTP request handling
- **[wiz.response](wiz-response.md)** - HTTP response generation
- **[wiz.project](wiz-project.md)** - Project management
- **[wiz.session](wiz-session.md)** - Session management
- **[wiz.fs()](wiz-filesystem.md)** - Filesystem access
- **[wiz.model()](wiz-model.md)** - Model loading
- **[wiz.controller()](wiz-controller.md)** - Controller loading
- **[wiz.logger()](wiz-logger.md)** - Logging

#### 2. [Utilities (season.util)](utilities.md)
Utility functions and classes available throughout the framework

- Logger
- Cache
- Filesystem
- String
- Compiler

### Frontend API (TypeScript)

#### 3. [Service API](service-api.md)
Service class API used in Angular components

- service.api - Backend API calls
- service.socket - WebSocket communication
- service.alert - Alerts and dialogs
- service.loading - Loading indicators
- service.render - Component rendering

### Configuration

#### 4. [Configuration](configuration.md)
Project configuration file structure and options

- boot.py
- ide.py
- service.py
- plugin.json

## 🚀 Quick Reference

### Frequently Used APIs

#### Get Request Data
```python
data = wiz.request.query()  # All parameters
name = wiz.request.query("name", "default")  # Specific parameter
```

#### Return JSON Response
```python
wiz.response.status(200, {"message": "Success"})
```

#### Handle File Upload
```python
files = wiz.request.files()
for key in files:
    file = files[key]
    # Process file
```

#### Session Management
```python
wiz.session.set("user_id", 123)
user_id = wiz.session.get("user_id")
```

#### Call Backend API (TypeScript)
```typescript
let res = await this.service.api.call("functionName", data);
```

## 📖 Documentation Conventions

### Parameter Notation

- **Required parameter**: `param` (bold)
- Optional parameter: `[param]` (in brackets)
- Default value: `param=value`

### Return Types

- `None` - Returns no value
- `str` - String
- `int` - Integer
- `dict` - Dictionary
- `list` - List
- `bool` - Boolean
- `object` - Object

### Example Code

Each API document includes practical usage examples.

## 🔍 Search Guide

### Finding APIs

1. **Request handling**: [wiz.request](wiz-request.md)
2. **Response generation**: [wiz.response](wiz-response.md)
3. **File operations**: [wiz.fs()](wiz-filesystem.md), [wiz.project.fs()](wiz-project.md)
4. **Database**: [wiz.model()](wiz-model.md)
5. **Session**: [wiz.session](wiz-session.md)
6. **Frontend communication**: [Service API](service-api.md)

## Version Information

This documentation is written based on the latest version of WIZ Framework (season).

## Contributing

If you find errors or missing content in the API documentation, please let us know through GitHub Issues.
