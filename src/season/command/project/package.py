import os
import json
from .base import BaseCommand


class PackageCommand(BaseCommand):
    """Package management commands"""
    
    def list(self, project="main"):
        """List packages"""
        if not self._validate_project_path():
            return
        
        portal_path = os.path.join(self._get_project_path(project), "src", "portal")
        if not self.fs.isdir(portal_path):
            print("No packages found.")
            return
        
        packages = self.fs.list(portal_path)
        print("Packages:")
        for p in packages:
            if self.fs.isdir(os.path.join(portal_path, p)):
                print(f"  - {p}")
    
    def create(self, namespace=None, project="main", title=None):
        """Create package"""
        if not self._validate_project_path():
            return
        
        if namespace is None:
            print("Package namespace is required. (--namespace=mypackage)")
            return
        
        package_path = self._get_portal_path(project, namespace)
        
        if self.fs.isdir(package_path):
            print(f"Package '{namespace}' already exists.")
            return
        
        print(f"Creating package '{namespace}'...")
        self.fs.makedirs(package_path)
        self.fs.makedirs(os.path.join(package_path, "app"))
        self.fs.makedirs(os.path.join(package_path, "controller"))
        self.fs.makedirs(os.path.join(package_path, "route"))
        
        # Create portal.json
        portal_data = {
            "package": namespace,
            "title": title if title else namespace.upper(),
            "version": "1.0.0",
            "use_app": True,
            "use_widget": True,
            "use_route": True,
            "use_libs": True,
            "use_styles": True,
            "use_assets": True,
            "use_controller": True,
            "use_model": True
        }
        self.fs.write(os.path.join(package_path, "portal.json"), json.dumps(portal_data, indent=4))
        
        # Create README.md
        readme_content = f"""# {title if title else namespace.upper()}

## Overview

{namespace} package for WIZ Framework.

## Version

- **Package**: {namespace}
- **Version**: 1.0.0

## Structure

```
{namespace}/
├── portal.json      # Package configuration
├── README.md        # This file
├── app/             # Application components
├── controller/      # Controllers
└── route/           # Routes
```

## Usage

This package can be used within WIZ Framework projects.

## License

MIT License
"""
        self.fs.write(os.path.join(package_path, "README.md"), readme_content)
        
        print(f"Package '{namespace}' created successfully.")
    
    def delete(self, namespace=None, project="main"):
        """Delete package"""
        if not self._validate_project_path():
            return
        
        if namespace is None:
            print("Package namespace is required.")
            return
        
        package_path = self._get_portal_path(project, namespace)
        
        if not self.fs.isdir(package_path):
            print(f"Package '{namespace}' does not exist.")
            return
        
        print(f"Deleting package '{namespace}'...")
        self.fs.remove(package_path)
        print(f"Package '{namespace}' deleted successfully.")
