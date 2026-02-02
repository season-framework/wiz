import os
import json
from .base import BaseCommand


class NpmCommand(BaseCommand):
    """NPM 패키지 관리 명령어"""
    
    def list(self):
        """npm 패키지 목록 조회"""
        if not self._validate_project_path():
            return
        
        package_json_path = "package.json"
        if not self.fs.exists(package_json_path):
            print("package.json not found.")
            return
        
        try:
            content = self.fs.read(package_json_path)
            data = json.loads(content)
            
            print("Dependencies:")
            deps = data.get("dependencies", {})
            for pkg, ver in deps.items():
                print(f"  {pkg}: {ver}")
            
            print("\nDev Dependencies:")
            dev_deps = data.get("devDependencies", {})
            for pkg, ver in dev_deps.items():
                print(f"  {pkg}: {ver}")
        except Exception as e:
            print(f"Error reading package.json: {e}")
    
    def install(self, package=None, version=None, dev=False):
        """npm 패키지 설치"""
        if not self._validate_project_path():
            return
        
        if package is None:
            # 전체 의존성 설치
            print("Installing all npm dependencies...")
            os.system("npm install")
            return
        
        pkg_spec = package
        if version:
            pkg_spec = f"{package}@{version}"
        
        dev_flag = "--save-dev" if dev else "--save"
        print(f"Installing npm package '{pkg_spec}'...")
        os.system(f"npm install {dev_flag} \"{pkg_spec}\"")
        print(f"Package '{pkg_spec}' installed successfully.")
    
    def uninstall(self, package=None):
        """npm 패키지 제거"""
        if not self._validate_project_path():
            return
        
        if package is None:
            print("Package name is required. (--package=@angular/core)")
            return
        
        print(f"Uninstalling npm package '{package}'...")
        os.system(f"npm uninstall {package}")
        print(f"Package '{package}' uninstalled successfully.")
    
    def update(self, package=None):
        """npm 패키지 업데이트"""
        if not self._validate_project_path():
            return
        
        if package:
            print(f"Updating npm package '{package}'...")
            os.system(f"npm update {package}")
        else:
            print("Updating all npm packages...")
            os.system("npm update")
        print("Update completed.")
