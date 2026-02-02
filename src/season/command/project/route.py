import os
from .base import BaseCommand


class RouteCommand(BaseCommand):
    """Route 관리 명령어"""
    
    def list(self, package=None):
        """라우트 목록 조회"""
        if not self._validate_project_path():
            return
        
        base_path = self._get_route_base_path(package)
        if not self.fs.isdir(base_path):
            print(f"No routes found in '{base_path}'.")
            return
        
        routes = self.fs.list(base_path)
        print(f"Routes in '{base_path}':")
        for r in routes:
            print(f"  - {r}")
    
    def create(self, name=None, package=None, route_path="/", methods=None, template="default"):
        """라우트 생성"""
        if not self._validate_project_path():
            return
        
        if name is None:
            print("Route name is required. (--name=api)")
            return
        
        base_path = self._get_route_base_path(package)
        file_path = os.path.join(base_path, f"{name}.py")
        
        if self.fs.exists(file_path):
            print(f"Route '{name}' already exists.")
            return
        
        self.fs.makedirs(base_path)
        
        methods = methods or "GET,POST"
        route_template = '''"""
Route: {name}
Path: {path}
Methods: {methods}
"""

def route(wiz):
    request = wiz.request
    response = wiz.response
    
    # Route logic here
    
    return response.status(200)
'''
        
        print(f"Creating route '{name}'...")
        self.fs.write(file_path, route_template.format(name=name, path=route_path, methods=methods))
        print(f"Route '{name}' created successfully.")
    
    def delete(self, name=None, package=None):
        """라우트 삭제"""
        if not self._validate_project_path():
            return
        
        if name is None:
            print("Route name is required.")
            return
        
        base_path = self._get_route_base_path(package)
        file_path = os.path.join(base_path, f"{name}.py")
        
        if not self.fs.exists(file_path):
            print(f"Route '{name}' does not exist.")
            return
        
        print(f"Deleting route '{name}'...")
        self.fs.remove(file_path)
        print(f"Route '{name}' deleted successfully.")
    
    def update(self, name=None, package=None, content=None):
        """라우트 업데이트"""
        if not self._validate_project_path():
            return
        
        if name is None:
            print("Route name is required.")
            return
        
        base_path = self._get_route_base_path(package)
        file_path = os.path.join(base_path, f"{name}.py")
        
        if not self.fs.exists(file_path):
            print(f"Route '{name}' does not exist.")
            return
        
        if content:
            print(f"Updating route '{name}'...")
            self.fs.write(file_path, content)
            print(f"Route '{name}' updated successfully.")
        else:
            print("Content is required for update.")
