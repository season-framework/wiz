<div align="center">

# WIZ Framework

**Modern Full-Stack Web Development Framework**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/pypi-season-blue)](https://pypi.org/project/season/)
[![Angular](https://img.shields.io/badge/angular-18-red)](https://angular.io/)

[Features](#-features) •
[Quick Start](#-quick-start) •
[Documentation](#-documentation) •
[Examples](#-examples) •
[Contributing](#-contributing)

![WIZ IDE Screenshot](./screenshot/wiz.gif)

</div>

---

## 📖 Overview

**WIZ** is a powerful full-stack web development framework that combines Python backend with Angular frontend, providing an integrated development environment (IDE) for rapid web application development. Built on Flask and Angular, WIZ simplifies the development workflow with its intuitive web-based IDE and comprehensive plugin system.

### Why WIZ?

- 🚀 **Rapid Development** - Create full-stack applications with minimal boilerplate
- 🎨 **Web-Based IDE** - Develop directly in your browser with a modern, feature-rich IDE
- 🔌 **Plugin Architecture** - Extend functionality with a powerful plugin system
- 📦 **Built-in Tools** - Git integration, npm/pip management, live preview, and more
- 🌐 **Full-Stack** - Python backend (Flask) + Angular frontend seamlessly integrated
- 🔧 **Flexible Configuration** - Easy project configuration and management

## ✨ Features

### Core Features
- **Web-Based IDE** - Full-featured development environment accessible through your browser
- **Hot Reload** - Instant preview of changes during development
- **Multiple Projects** - Manage multiple projects within a single workspace
- **Component Generator** - Quickly scaffold pages, components, and services
- **API Development** - Streamlined backend API development with Flask
- **Portal Framework** - Create and manage reusable module packages

### Built-in Tools
- 📁 **File Explorer** - Browse and manage project files
- 💻 **Code Editor** - Monaco-based editor with syntax highlighting and autocomplete
- 🔍 **Search & Replace** - Powerful search across your entire project
- 🌳 **Git Integration** - Version control directly in the IDE
- 📦 **Package Management** - npm and pip package management UI
- 🖼️ **Asset Preview** - Preview images and other assets
- 🤖 **AI Assistant** - GPT-powered coding assistant (optional)

### Developer Experience
- **TypeScript Support** - Full TypeScript support for Angular development
- **Pug Templates** - Option to use Pug for cleaner HTML templates
- **TailwindCSS** - Built-in support for TailwindCSS
- **Socket.IO** - Real-time communication support
- **WSGI Compatible** - Production-ready WSGI deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm

### Installation

1. **Install Node.js and npm** (if not already installed):
```bash
apt install nodejs npm
npm i -g n
n stable
apt purge nodejs npm
```

2. **Install WIZ**:
```bash
pip install season             # Install
pip install season --upgrade   # Upgrade to latest
```

### Create Your First Project

```bash
# Create a new project
cd <workspace>
wiz create myapp
cd myapp

# Start development server
wiz run --port 3000

# Open your browser to http://127.0.0.1:3000/wiz
```

### Development Mode

```bash
# Start development server with custom settings
wiz run --host=0.0.0.0 --port=3000 --log=wiz.log
```

### Production Mode

```bash
# Start as daemon
wiz server start
wiz server stop
wiz server restart

# Register as system service (Linux)
wiz service regist myapp
wiz service start myapp
```

### Upgrade

```bash
pip install season --upgrade  # Upgrade core framework
wiz ide upgrade               # Upgrade IDE components
```

## 📚 Documentation

Comprehensive documentation is available in multiple languages:

- **[English Documentation](docs/en/)** - Complete guide in English
  - [Usage Guide](docs/en/usage-guide.md) - Getting started and development guide
  - [Architecture](docs/en/architecture.md) - Framework design and internals
  - [API Reference](docs/en/api/README.md) - Complete API documentation
  - [Examples](docs/en/examples.md) - Practical examples and tutorials

- **[한국어 문서](docs/kr/)** - 한국어 완전 가이드
  - [사용 가이드](docs/kr/usage-guide.md) - 시작 및 개발 가이드
  - [아키텍처](docs/kr/architecture.md) - 프레임워크 설계 및 내부 구조
  - [API 레퍼런스](docs/kr/api/README.md) - 전체 API 문서
  - [예제 모음](docs/kr/examples.md) - 실전 예제 및 튜토리얼

## 💻 CLI Reference

### Project Management

#### Create Project
```bash
wiz create [Project Name]
```

#### Run Project
```bash
# Development server
wiz run --host=<host> --port=<port> --log=<log file path>

# Available flags:
# --port: Web server port (default: 3000)
# --host: Web server host (default: 0.0.0.0)
# --log: Log file path (default: None)
```

#### Bundle Project
```bash
wiz bundle                    # Bundle main project
wiz bundle --project=main     # Bundle specific project
```

### Daemon Management

```bash
wiz server start [--log=PATH] [--force]   # Start daemon
wiz server stop                            # Stop daemon
wiz server restart                         # Restart daemon
```

### Service Management (Linux)

```bash
wiz service list                          # List all services
wiz service regist <name> [port]          # Register service
wiz service unregist <name>               # Unregister service
wiz service status <name>                 # Check service status
wiz service start [name]                  # Start service(s)
wiz service stop [name]                   # Stop service(s)
wiz service restart [name]                # Restart service(s)
```

### Plugin Commands

```bash
wiz command <plugin name> <args>          # Execute plugin command
```

## 🎯 Examples

### Creating a Simple API

```python
# In your controller file (e.g., controller/api.py)
def index(wiz):
    return wiz.response.json({"message": "Hello, WIZ!"})
```

### Creating an Angular Component

Use the built-in IDE to:
1. Navigate to the workspace explorer
2. Click "New Component"
3. Enter component details
4. The framework automatically generates the component structure

For more examples, see the [Examples Documentation](docs/en/examples.md).

## 🏗️ Architecture

WIZ follows a modular architecture:

```
project/
├── app/                    # Angular applications
│   ├── component.ts        # Component logic
│   ├── view.pug           # Component template (Pug)
│   └── view.html          # Component template (HTML)
├── controller/            # Backend controllers
├── model/                 # Data models
├── route/                 # Custom routes
├── portal/                # Reusable modules
└── config/                # Configuration files
```

For detailed architecture information, see [Architecture Documentation](docs/en/architecture.md).

## 🔌 Plugin System

WIZ supports a powerful plugin system for extending functionality:

- **Core Plugins** - Essential IDE functionality
- **Workspace Plugins** - Project management and file operations
- **Git Plugins** - Version control integration
- **Utility Plugins** - Additional tools and features
- **Custom Plugins** - Create your own plugins

## 📋 Version Policy

WIZ follows semantic versioning (`x.y.z`):

- **`x` (Major)**: Breaking changes - upgrade not supported
- **`y` (Minor)**: New features - requires server restart
- **`z` (Patch)**: UI updates - can be upgraded without restart

## 📝 Release Notes

See [RELEASES.md](RELEASES.md) for the latest updates and complete version history.

Quick links to version-specific releases:
- [Version 2.4.x (Current)](releases/v2.4.md) - Angular 18, TailwindCSS, AI Assistant
- [Version 2.3.x](releases/v2.3.md) - Bundle structure, Angular 17
- [Version 2.2.x](releases/v2.2.md) - IDE overlay menu
- [Version 2.1.x](releases/v2.1.md) - IDE plugin concept
- [Version 2.0.x](releases/v2.0.md) - Angular 14, UI/UX redesign
- [Version 1.0.x and earlier](releases/v1.0.md) - Legacy releases

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

### Development Setup

1. Clone the repository
```bash
git clone https://github.com/season-framework/wiz.git
cd wiz
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run in development mode
```bash
cd src
python -m season.cmd run
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/) and [Angular](https://angular.io/)
- Code editor powered by [Monaco Editor](https://microsoft.github.io/monaco-editor/)
- Terminal powered by [xterm.js](https://xtermjs.org/)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/season-framework/wiz/issues)
- **Documentation**: [docs/](docs/)

---

<div align="center">

Made with ❤️ by the WIZ Framework Team

[⬆ Back to Top](#wiz-framework)

</div>

