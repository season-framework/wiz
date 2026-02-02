# WIZ Command Guide

The WIZ framework provides various CLI commands for project creation, development, building, and deployment.

## Table of Contents

- [Basic Commands](#basic-commands)
  - [wiz create](#wiz-create)
  - [wiz run](#wiz-run)
  - [wiz build](#wiz-build)
  - [wiz server](#wiz-server)
  - [wiz bundle](#wiz-bundle)
  - [wiz kill](#wiz-kill)
- [IDE Management](#ide-management)
  - [wiz ide](#wiz-ide)
- [Service Management](#service-management)
  - [wiz service](#wiz-service)
- [Project Management](#project-management)
  - [wiz project](#wiz-project)
  - [wiz project app](#wiz-project-app)
  - [wiz project controller](#wiz-project-controller)
  - [wiz project route](#wiz-project-route)
  - [wiz project package](#wiz-project-package)
  - [wiz project npm](#wiz-project-npm)

---

## Basic Commands

### wiz create

Creates a new WIZ workspace.

```bash
wiz create <projectname>
```

**Example:**

```bash
# Create 'myapp' workspace
wiz create myapp
```

**Generated structure:**
- `config/` - Configuration files
- `public/` - Web server files
- `ide/` - WIZ IDE
- `plugin/` - Plugins
- `project/` - Project folder

---

### wiz run

Runs the development server.

```bash
wiz run [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--host` | Host address to bind | `0.0.0.0` |
| `--port` | Server port | `3000` |
| `--bundle` | Run in bundle mode | `false` |
| `--log` | Log file path | - |

**Examples:**

```bash
# Default run (0.0.0.0:3000)
wiz run

# Run on custom port
wiz run --port=8080

# Run on specific host
wiz run --host=127.0.0.1

# Run in bundle mode
wiz run --bundle

# Specify log file
wiz run --log=server.log
```

---

### wiz server

Manages the server as a daemon (background process).

```bash
wiz server <action> [options]
```

**Actions:**

| Action | Description |
|--------|-------------|
| `start` | Start server as daemon |
| `stop` | Stop daemon server |
| `restart` | Restart daemon server |

**Options:**

| Option | Description |
|--------|-------------|
| `--log` | Log file path |
| `--force` | Force start (remove stale PID) |

**Examples:**

```bash
# Start daemon
wiz server start

# Start with log file
wiz server start --log=/var/log/wiz.log

# Force start (remove stale PID)
wiz server start --force

# Stop daemon
wiz server stop

# Restart daemon
wiz server restart
```

---

### wiz bundle

Creates a deployment bundle.

```bash
wiz bundle [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--project` | Project name | `main` |

**Examples:**

```bash
# Bundle default project
wiz bundle

# Bundle specific project
wiz bundle --project=dev
```

**Generated bundle structure:**
```
bundle/
├── project/main/bundle/
├── config/
├── public/
└── plugin/
```

---

### wiz kill

Terminates all WIZ processes.

```bash
wiz kill
```

---

## IDE Management

### wiz ide

Manages WIZ IDE.

```bash
wiz ide <action>
```

**Actions:**

| Action | Description |
|--------|-------------|
| `install` | Install WIZ IDE |
| `remove` | Remove WIZ IDE |
| `upgrade` | Upgrade WIZ IDE |
| `build` | Build WIZ IDE |
| `clean` | Clean WIZ IDE cache |

**Examples:**

```bash
# Install IDE
wiz ide install

# Remove IDE
wiz ide remove

# Upgrade IDE
wiz ide upgrade

# Build IDE
wiz ide build

# Clean IDE cache
wiz ide clean
```

---

## Service Management

### wiz service

Manages WIZ as a Linux systemd service. (Linux only)

```bash
wiz service <action> [name] [options]
```

**Actions:**

| Action | Description |
|--------|-------------|
| `regist` | Register service |
| `unregist` | Unregister service |
| `start` | Start service |
| `stop` | Stop service |
| `restart` | Restart service |
| `status` | Check service status |
| `list` | List registered services |

**Examples:**

```bash
# Register service
wiz service regist myapp

# Register service with specific port
wiz service regist myapp 8080

# Register service in bundle mode
wiz service regist myapp 8080 bundle

# Start service
wiz service start myapp

# Start all services
wiz service start

# Stop service
wiz service stop myapp

# Restart service
wiz service restart myapp

# Check service status
wiz service status myapp

# List services
wiz service list

# Unregister service
wiz service unregist myapp
```

**Service file paths:**
- Executable: `/usr/local/bin/wiz.<name>`
- Service file: `/etc/systemd/system/wiz.<name>.service`
- Log file: `/var/log/wiz/<name>`

---

## Project Management

### wiz project

Manages projects.

```bash
wiz project <subcommand> [action] [options]
```

#### Project Core Commands

| Command | Description |
|---------|-------------|
| `build` | Build project |
| `create` | Create project |
| `delete` | Delete project |
| `list` | List projects |
| `clean` | Clean project cache |
| `export` | Export project (.wizproject) |

**Examples:**

```bash
# Build project
wiz project build --project=main

# Clean build
wiz project build --project=main --clean

# Create new project
wiz project create --project=dev

# Create project from Git
wiz project create --project=dev --uri=https://github.com/user/repo.git

# Create project from .wizproject file
wiz project create --project=dev --path=/path/to/backup.wizproject

# Delete project
wiz project delete --project=dev

# List projects
wiz project list

# Clean project cache
wiz project clean --project=main

# Export project
wiz project export --project=main --output=backup.wizproject
```

---

### wiz project app

Manages apps.

```bash
wiz project app <action> [options]
```

**Actions:**

| Action | Description |
|--------|-------------|
| `list` | List apps |
| `create` | Create app |
| `delete` | Delete app |

**Options:**

| Option | Description |
|--------|-------------|
| `--namespace` | App namespace (e.g., main.dashboard) |
| `--project` | Project name (default: main) |
| `--package` | Portal package name |

**Examples:**

```bash
# List apps
wiz project app list

# List apps in package
wiz project app list --package=myportal

# Create app
wiz project app create --namespace=main.dashboard

# Create app in package
wiz project app create --namespace=main.dashboard --package=myportal

# Delete app
wiz project app delete --namespace=main.dashboard
```

**Generated files:**
```
app/<namespace>/
├── app.json      # App configuration
├── view.ts       # Component logic
└── view.html     # Template
```

---

### wiz project controller

Manages controllers.

```bash
wiz project controller <action> [options]
```

**Actions:**

| Action | Description |
|--------|-------------|
| `list` | List controllers |
| `create` | Create controller |
| `delete` | Delete controller |

**Options:**

| Option | Description |
|--------|-------------|
| `--namespace` | Controller name |
| `--project` | Project name (default: main) |
| `--package` | Portal package name |

**Examples:**

```bash
# List controllers
wiz project controller list

# Create controller
wiz project controller create --namespace=api

# Create controller in package
wiz project controller create --namespace=api --package=myportal

# Delete controller
wiz project controller delete --namespace=api
```

---

### wiz project route

Manages routes.

```bash
wiz project route <action> [options]
```

**Actions:**

| Action | Description |
|--------|-------------|
| `list` | List routes |
| `create` | Create route |
| `delete` | Delete route |

**Options:**

| Option | Description |
|--------|-------------|
| `--namespace` | Route name |
| `--project` | Project name (default: main) |
| `--package` | Portal package name |
| `--path` | Route path |
| `--methods` | HTTP methods (default: GET,POST) |

**Examples:**

```bash
# List routes
wiz project route list

# Create route
wiz project route create --namespace=api

# Create route with path
wiz project route create --namespace=api --path=/api/v1

# Delete route
wiz project route delete --namespace=api
```

**Generated files:**
```
route/<namespace>/
├── app.json      # Route configuration
└── route.py      # Route handler
```

---

### wiz project package

Manages portal packages.

```bash
wiz project package <action> [options]
```

**Actions:**

| Action | Description |
|--------|-------------|
| `list` | List packages |
| `create` | Create package |
| `delete` | Delete package |

**Options:**

| Option | Description |
|--------|-------------|
| `--namespace` | Package name |
| `--project` | Project name (default: main) |

**Examples:**

```bash
# List packages
wiz project package list

# Create package
wiz project package create --namespace=myportal

# Delete package
wiz project package delete --namespace=myportal
```

**Generated structure:**
```
portal/<namespace>/
├── portal.json    # Package configuration
├── README.md      # Package documentation
├── app/           # Apps folder
├── controller/    # Controllers folder
└── route/         # Routes folder
```

---

### wiz project npm

Manages NPM packages. (Based on project build folder)

```bash
wiz project npm <action> [options]
```

**Actions:**

| Action | Description |
|--------|-------------|
| `list` | List packages |
| `install` | Install package |
| `uninstall` | Uninstall package |

**Options:**

| Option | Description |
|--------|-------------|
| `--package` | Package name |
| `--version` | Package version |
| `--dev` | Install as dev dependency |
| `--project` | Project name (default: main) |

**Examples:**

```bash
# List packages
wiz project npm list

# Install all dependencies
wiz project npm install

# Install specific package
wiz project npm install --package=@angular/core

# Install with version
wiz project npm install --package=@angular/core --version=^18.2.5

# Install as dev dependency
wiz project npm install --package=typescript --dev

# Uninstall package
wiz project npm uninstall --package=@angular/core
```

> **Note:** NPM commands are executed in the `project/<name>/build` folder, and `package.json` is synced to `src/angular/package.json` after operations.

---

## Common Options

### --version

Check WIZ version.

```bash
wiz --version
```

### --help

View command help.

```bash
wiz --help
wiz <command> --help
```

---

## Workflow Examples

### Starting a New Project

```bash
# 1. Create workspace
wiz create myapp

# 2. Navigate to workspace
cd myapp

# 3. Run development server
wiz run
```

### Project Development

```bash
# Create new app
wiz project app create --namespace=main.dashboard

# Create controller
wiz project controller create --namespace=api

# Create route
wiz project route create --namespace=api --path=/api

# Build project
wiz project build
```

### Deployment Preparation

```bash
# Create project bundle
wiz bundle --project=main

# Or export project
wiz project export --project=main --output=backup.wizproject
```

### Production Server (Linux)

```bash
# Register service
wiz service regist myapp 80

# Start service
wiz service start myapp

# Check service status
wiz service status myapp
```
