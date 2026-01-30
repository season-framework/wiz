# WIZ Framework Documentation

Comprehensive documentation for the WIZ framework.

## 📚 Table of Contents

### 1. [Usage Guide](usage-guide.md)
Complete guide to getting started with the WIZ framework.

- **Installation**: How to install Python, Node.js, and the WIZ framework
- **Project Creation**: Creating a new project and understanding the initial structure
- **Server Execution**: Running the server in development/production mode
- **Page Creation**: How to create new pages and components
- **API Development**: Writing and using backend APIs
- **Adding Routes**: Creating independent API endpoints
- **Writing Models**: Implementing data models and business logic
- **Using Portals**: Leveraging reusable module packages
- **Build and Deployment**: Deploying to production environments

### 2. [Architecture](architecture.md)
Explains the internal structure and design principles of the WIZ framework.

- **Overview**: Introduction to the WIZ framework
- **Core Components**: Season package structure
- **Server Architecture**: Server class and project structure
- **Project Internal Structure**: app, controller, model, route, portal
- **Configuration System**: boot.py and configuration management
- **Plugin System**: Extensible plugin architecture
- **IDE Integration**: Web-based IDE environment
- **Build System**: Angular build process
- **Communication Architecture**: HTTP and WebSocket communication
- **Data Flow**: Request-response flow
- **Scalability and Security**: Scaling and security considerations

### 3. [API Reference](api/README.md)
Complete API documentation for the WIZ framework.

#### Backend API (Python)
- **[wiz.request](api/wiz-request.md)** - HTTP request handling
- **[wiz.response](api/wiz-response.md)** - HTTP response generation
- **[wiz.project](api/wiz-project.md)** - Project management and filesystem
- **[wiz.session](api/wiz-session.md)** - Session management
- **[wiz.model()](api/wiz-model.md)** - Model loading
- **[wiz.fs()](api/wiz-filesystem.md)** - Filesystem access

#### Frontend API (TypeScript)
- **[Service API](api/service-api.md)** - Angular component service

### 4. [Examples](examples.md)
Learning guide through practical examples.

- Basic page creation
- API communication
- File upload/download
- WebSocket real-time communication
- Database integration
- Session management
- RESTful API
- Image processing
- CSV/Excel file processing
- Authentication system

## 🚀 Quick Start

### Installation

```bash
# Install WIZ framework
pip install season
```

### Project Creation

```bash
# Create a new project
wiz create myapp
cd myapp
```

### Server Execution

```bash
# Start development server
wiz run --port=3000

# Access in browser
# http://127.0.0.1:3000/wiz
```

## 💡 Key Features

### 1. Full-Stack Framework
- **Backend**: Python Flask-based
- **Frontend**: Angular-based
- **Real-time Communication**: SocketIO support

### 2. Web-based IDE
- Develop directly in the browser
- File explorer, code editor, terminal provided
- Real-time preview

### 3. Modular Structure
- **App**: Angular components (pages, layouts, widgets)
- **Controller**: Backend logic
- **Model**: Data models
- **Route**: API endpoints
- **Portal**: Reusable modules

### 4. Plugin System
- Extensible architecture
- Custom CLI commands
- IDE functionality extensions

## 📁 Project Structure

```
myapp/
├── config/              # Configuration files
│   └── boot.py          # Server boot configuration
├── public/              # Public directory
│   └── app.py           # Entry point
├── project/             # Projects
│   └── main/            # Main project
│       └── src/         # Source code
│           ├── app/     # Angular components
│           ├── controller/  # Controllers
│           ├── model/   # Models
│           ├── route/   # API routes
│           └── portal/  # Portals
├── ide/                 # WIZ IDE
└── plugin/              # Plugins
```

## 🔧 Development Workflow

### 1. Page Creation

```bash
# Create in IDE or manually
project/main/src/app/page.mypage/
├── view.pug     # Template
├── view.ts      # Logic
├── view.scss    # Styles
├── app.json     # Metadata
├── api.py       # Backend API
└── socket.py    # WebSocket handler
```

### 2. API Writing

**api.py**
```python
def load():
    data = {"message": "Hello"}
    wiz.response.status(200, data)
```

**view.ts**
```typescript
async loadData() {
    let res = await this.service.api.call("load");
    console.log(res.data);
}
```

### 3. Build and Test

```bash
# Build
wiz command workspace build main

# Run server
wiz run --port=3000

# Access
http://127.0.0.1:3000/mypage
```

## 📖 Learning Path

1. **Beginner**: Follow the [Usage Guide](usage-guide.md) from installation to page creation
2. **Intermediate**: Learn API development, model writing, and route addition
3. **Advanced**: Understand internal structure through the [Architecture](architecture.md) documentation, develop plugins

## 🔗 Related Links

- **GitHub**: https://github.com/season-framework/wiz
- **PyPI**: https://pypi.org/project/season/
- **License**: MIT License

## 🤝 Contributing

The WIZ framework is an open-source project. Contributions are welcome!

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

MIT License - Free to use, modify, and distribute.

## 📞 Support

- **Issue Reporting**: [GitHub Issues](https://github.com/season-framework/wiz/issues)
- **Email**: proin@season.co.kr

---

**Copyright 2021 SEASON CO. LTD.**
