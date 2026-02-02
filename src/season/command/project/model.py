import os
from .base import BaseCommand


class ModelCommand(BaseCommand):
    """Model 관리 명령어"""
    
    def list(self, package=None):
        """모델 목록 조회"""
        if not self._validate_project_path():
            return
        
        base_path = self._get_model_base_path(package)
        if not self.fs.isdir(base_path):
            print(f"No models found in '{base_path}'.")
            return
        
        models = self.fs.list(base_path)
        print(f"Models in '{base_path}':")
        for m in models:
            print(f"  - {m}")
    
    def create(self, name=None, package=None, template="default"):
        """모델 생성"""
        if not self._validate_project_path():
            return
        
        if name is None:
            print("Model name is required. (--name=user)")
            return
        
        base_path = self._get_model_base_path(package)
        model_path = os.path.join(base_path, f"{name}.py")
        
        if self.fs.exists(model_path):
            print(f"Model '{name}' already exists.")
            return
        
        self.fs.makedirs(base_path)
        
        model_template = '''"""
Model: {name}
"""

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
    
    def get(self, id=None):
        pass
    
    def list(self, **kwargs):
        pass
    
    def create(self, data):
        pass
    
    def update(self, id, data):
        pass
    
    def delete(self, id):
        pass
'''
        
        print(f"Creating model '{name}'...")
        self.fs.write(model_path, model_template.format(name=name))
        print(f"Model '{name}' created successfully.")
    
    def delete(self, name=None, package=None):
        """모델 삭제"""
        if not self._validate_project_path():
            return
        
        if name is None:
            print("Model name is required.")
            return
        
        base_path = self._get_model_base_path(package)
        model_path = os.path.join(base_path, f"{name}.py")
        
        if not self.fs.exists(model_path):
            print(f"Model '{name}' does not exist.")
            return
        
        print(f"Deleting model '{name}'...")
        self.fs.remove(model_path)
        print(f"Model '{name}' deleted successfully.")
    
    def update(self, name=None, package=None, content=None):
        """모델 업데이트"""
        if not self._validate_project_path():
            return
        
        if name is None:
            print("Model name is required.")
            return
        
        base_path = self._get_model_base_path(package)
        model_path = os.path.join(base_path, f"{name}.py")
        
        if not self.fs.exists(model_path):
            print(f"Model '{name}' does not exist.")
            return
        
        if content:
            print(f"Updating model '{name}'...")
            self.fs.write(model_path, content)
            print(f"Model '{name}' updated successfully.")
        else:
            print("Content is required for update.")
