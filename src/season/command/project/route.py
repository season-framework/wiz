import os
import json
from .base import BaseCommand


class RouteCommand(BaseCommand):
    """Route management commands"""
    
    def list(self, project="main", package=None):
        """List routes"""
        if not self._validate_project_path():
            return
        
        base_path = self._get_route_base_path(project, package)
        if not self.fs.isdir(base_path):
            print(f"No routes found in '{base_path}'.")
            return
        
        routes = self.fs.list(base_path)
        print(f"Routes in '{base_path}':")
        for r in routes:
            print(f"  - {r}")
    
    def create(self, namespace=None, project="main", package=None, route_path=None, methods=None, template="default"):
        """Create route"""
        if not self._validate_project_path():
            return
        
        if namespace is None:
            print("Route namespace is required. (--namespace=api)")
            return
        
        base_path = self._get_route_base_path(project, package)
        route_dir = os.path.join(base_path, namespace)
        
        if self.fs.isdir(route_dir):
            print(f"Route '{namespace}' already exists.")
            return
        
        print(f"Creating route '{namespace}'...")
        self.fs.makedirs(route_dir)
        
        # Create app.json
        app_data = {
            "id": namespace,
            "title": namespace,
            "route": route_path if route_path else namespace,
            "viewuri": "",
            "category": ""
        }
        self.fs.write(os.path.join(route_dir, "app.json"), json.dumps(app_data, indent=4))
        
        # Create route.py
        methods = methods or "GET,POST"
        route_template = '''"""
Route: {name}
Path: {path}
Methods: {methods}
"""
segment = wiz.request.match("/{route}/<action>/<path:path>")
action = segment.action
value = wiz.request.get("value")
wiz.response.status(200, value)
'''
        
        self.fs.write(os.path.join(route_dir, "route.py"), route_template.format(
            name=namespace, 
            path=route_path if route_path else namespace, 
            methods=methods,
            route=route_path if route_path else namespace
        ))
        print(f"Route '{namespace}' created successfully.")
    
    def delete(self, namespace=None, project="main", package=None):
        """Delete route"""
        if not self._validate_project_path():
            return
        
        if namespace is None:
            print("Route namespace is required.")
            return
        
        base_path = self._get_route_base_path(project, package)
        route_dir = os.path.join(base_path, namespace)
        
        if not self.fs.isdir(route_dir):
            print(f"Route '{namespace}' does not exist.")
            return
        
        print(f"Deleting route '{namespace}'...")
        self.fs.remove(route_dir)
        print(f"Route '{namespace}' deleted successfully.")
