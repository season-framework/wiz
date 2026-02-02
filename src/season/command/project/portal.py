import os
from .base import BaseCommand


class PortalCommand(BaseCommand):
    """Portal 관리 명령어 (MCP 확장용)"""
    
    def list(self):
        """포탈 패키지 목록 조회"""
        if not self._validate_project_path():
            return
        
        if not self.fs.isdir(self.portal_base):
            print("No portal packages found.")
            return
        
        portals = self.fs.list(self.portal_base)
        print("Portal packages:")
        for p in portals:
            if self.fs.isdir(os.path.join(self.portal_base, p)):
                print(f"  - {p}")
    
    def create(self, name=None):
        """포탈 패키지 생성"""
        if not self._validate_project_path():
            return
        
        if name is None:
            print("Portal name is required. (--name=myportal)")
            return
        
        portal_path = self._get_portal_path(name)
        
        if self.fs.isdir(portal_path):
            print(f"Portal '{name}' already exists.")
            return
        
        print(f"Creating portal '{name}'...")
        self.fs.makedirs(os.path.join(portal_path, "app"))
        self.fs.makedirs(os.path.join(portal_path, "controller"))
        self.fs.makedirs(os.path.join(portal_path, "model"))
        self.fs.makedirs(os.path.join(portal_path, "route"))
        print(f"Portal '{name}' created successfully.")
    
    def delete(self, name=None):
        """포탈 패키지 삭제"""
        if not self._validate_project_path():
            return
        
        if name is None:
            print("Portal name is required.")
            return
        
        portal_path = self._get_portal_path(name)
        
        if not self.fs.isdir(portal_path):
            print(f"Portal '{name}' does not exist.")
            return
        
        print(f"Deleting portal '{name}'...")
        self.fs.remove(portal_path)
        print(f"Portal '{name}' deleted successfully.")
    
    def info(self, name=None):
        """포탈 패키지 정보 조회"""
        if not self._validate_project_path():
            return
        
        if name is None:
            print("Portal name is required.")
            return
        
        portal_path = self._get_portal_path(name)
        
        if not self.fs.isdir(portal_path):
            print(f"Portal '{name}' does not exist.")
            return
        
        print(f"Portal: {name}")
        print(f"Path: {portal_path}")
        
        # 구성 요소 카운트
        app_count = len(self.fs.list(os.path.join(portal_path, "app"))) if self.fs.isdir(os.path.join(portal_path, "app")) else 0
        controller_count = len(self.fs.list(os.path.join(portal_path, "controller"))) if self.fs.isdir(os.path.join(portal_path, "controller")) else 0
        model_count = len(self.fs.list(os.path.join(portal_path, "model"))) if self.fs.isdir(os.path.join(portal_path, "model")) else 0
        route_count = len(self.fs.list(os.path.join(portal_path, "route"))) if self.fs.isdir(os.path.join(portal_path, "route")) else 0
        
        print(f"Apps: {app_count}")
        print(f"Controllers: {controller_count}")
        print(f"Models: {model_count}")
        print(f"Routes: {route_count}")
