import os
import json
from .base import BaseCommand


class AppCommand(BaseCommand):
    """App management commands"""
    
    def list(self, project="main", package=None):
        """List apps"""
        if not self._validate_project_path():
            return
        
        base_path = self._get_app_base_path(project, package)
        if not self.fs.isdir(base_path):
            print(f"No apps found in '{base_path}'.")
            return
        
        apps = self.fs.list(base_path)
        print(f"Apps in '{base_path}':")
        for app in apps:
            print(f"  - {app}")
    
    def create(self, namespace=None, project="main", package=None, engine="html", mode="page"):
        """
        Create app
        - namespace: App namespace (e.g., main.dashboard)
        - project: Project name (default: main)
        - package: Portal package name (if empty: src/app, if set: portal/<package>/app)
        - engine: Template engine (html, pug)
        - mode: App mode (page, component, layout)
        """
        if not self._validate_project_path():
            return
        
        if namespace is None:
            print("Namespace is required. (--namespace=main.dashboard)")
            return
        
        base_path = self._get_app_base_path(project, package)
        app_path = os.path.join(base_path, self._namespace_to_path(namespace))
        
        if self.fs.isdir(app_path):
            print(f"App '{namespace}' already exists at '{app_path}'.")
            return
        
        print(f"Creating app '{namespace}' at '{app_path}'...")
        self.fs.makedirs(app_path)
        
        # Create app.json
        app_data = {
            "mode": mode,
            "id": namespace,
            "title": namespace,
            "namespace": namespace,
            "viewuri": "/" + namespace.replace(".", "/"),
            "category": "",
            "controller": "",
            "template": ""
        }
        self.fs.write(os.path.join(app_path, "app.json"), json.dumps(app_data, indent=4))
        
        # Create view.ts
        view_ts = """import { OnInit, Input } from '@angular/core';

export class Component implements OnInit {
    @Input() title: any;

    public async ngOnInit() {
    }
}"""
        self.fs.write(os.path.join(app_path, "view.ts"), view_ts)
        
        # Create view.[engine]
        if engine == 'pug':
             self.fs.write(os.path.join(app_path, "view.pug"), "div\n    span {{title}}")
        else:
             self.fs.write(os.path.join(app_path, "view.html"), "<div>\n    <span>{{title}}</span>\n</div>")
        
        print(f"App '{namespace}' created successfully.")
    
    def delete(self, namespace=None, project="main", package=None):
        """Delete app"""
        if not self._validate_project_path():
            return
        
        if namespace is None:
            print("Namespace is required.")
            return
        
        base_path = self._get_app_base_path(project, package)
        app_path = os.path.join(base_path, self._namespace_to_path(namespace))
        
        if not self.fs.isdir(app_path):
            print(f"App '{namespace}' does not exist.")
            return
        
        print(f"Deleting app '{namespace}'...")
        self.fs.remove(app_path)
        print(f"App '{namespace}' deleted successfully.")
    

