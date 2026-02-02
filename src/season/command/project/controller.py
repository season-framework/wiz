import os
from .base import BaseCommand


class ControllerCommand(BaseCommand):
    """Controller management commands"""
    
    def list(self, project="main", package=None):
        """List controllers"""
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
    
    def create(self, namespace=None, project="main", package=None, template="default"):
        """Create controller"""
        if not self._validate_project_path():
            return
        
        if namespace is None:
            print("Controller namespace is required. (--namespace=api)")
            return
        
        base_path = self._get_controller_base_path(project, package)
        controller_path = os.path.join(base_path, f"{namespace}.py")
        
        if self.fs.exists(controller_path):
            print(f"Controller '{namespace}' already exists.")
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
        
        print(f"Creating controller '{namespace}'...")
        self.fs.write(controller_path, controller_template.format(namespace=namespace))
        print(f"Controller '{namespace}' created successfully.")
    
    def delete(self, namespace=None, project="main", package=None):
        """Delete controller"""
        if not self._validate_project_path():
            return
        
        if namespace is None:
            print("Controller namespace is required.")
            return
        
        base_path = self._get_controller_base_path(project, package)
        controller_path = os.path.join(base_path, f"{namespace}.py")
        
        if not self.fs.exists(controller_path):
            print(f"Controller '{namespace}' does not exist.")
            return
        
        print(f"Deleting controller '{namespace}'...")
        self.fs.remove(controller_path)
        print(f"Controller '{namespace}' deleted successfully.")