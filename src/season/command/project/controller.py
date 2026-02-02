import os
from .base import BaseCommand


class ControllerCommand(BaseCommand):
    """Controller 관리 명령어"""
    
    def list(self, project="main", package=None):
        """컨트롤러 목록 조회"""
        if not self._validate_project_path():
            return
        
        base_path = self._get_controller_base_path(project, package)
        if not self.fs.isdir(base_path):
            print(f"No controllers found in '{base_path}'.")
            return
        
        controllers = self.fs.list(base_path)
        print(f"Controllers in '{base_path}':")
        for c in controllers:
            print(f"  - {c}")
    
    def create(self, name=None, project="main", package=None, template="default"):
        """컨트롤러 생성"""
        if not self._validate_project_path():
            return
        
        if name is None:
            print("Controller name is required. (--name=api)")
            return
        
        base_path = self._get_controller_base_path(project, package)
        controller_path = os.path.join(base_path, f"{name}.py")
        
        if self.fs.exists(controller_path):
            print(f"Controller '{name}' already exists.")
            return
        
        self.fs.makedirs(base_path)
        
        controller_template = '''import season
import datetime
import json
import os

class Controller:
    def __init__(self):
        wiz.session = wiz.model("portal/season/session").use()
        sessiondata = wiz.session.get()
        wiz.response.data.set(session=sessiondata)

        lang = wiz.request.query("lang", None)
        if lang is not None:
            wiz.response.lang(lang)
            wiz.response.redirect(wiz.request.uri())

    def json_default(self, value):
        if isinstance(value, datetime.date):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return str(value).replace('<', '&lt;').replace('>', '&gt;')

'''
        
        print(f"Creating controller '{name}'...")
        self.fs.write(controller_path, controller_template.format(name=name))
        print(f"Controller '{name}' created successfully.")
    
    def delete(self, name=None, project="main", package=None):
        """컨트롤러 삭제"""
        if not self._validate_project_path():
            return
        
        if name is None:
            print("Controller name is required.")
            return
        
        base_path = self._get_controller_base_path(project, package)
        controller_path = os.path.join(base_path, f"{name}.py")
        
        if not self.fs.exists(controller_path):
            print(f"Controller '{name}' does not exist.")
            return
        
        print(f"Deleting controller '{name}'...")
        self.fs.remove(controller_path)
        print(f"Controller '{name}' deleted successfully.")
    
    def update(self, name=None, project="main", package=None, content=None):
        """컨트롤러 업데이트"""
        if not self._validate_project_path():
            return
        
        if name is None:
            print("Controller name is required.")
            return
        
        base_path = self._get_controller_base_path(project, package)
        controller_path = os.path.join(base_path, f"{name}.py")
        
        if not self.fs.exists(controller_path):
            print(f"Controller '{name}' does not exist.")
            return
        
        if content:
            print(f"Updating controller '{name}'...")
            self.fs.write(controller_path, content)
            print(f"Controller '{name}' updated successfully.")
        else:
            print("Content is required for update.")
