import os
from .base import BaseCommand


class PipCommand(BaseCommand):
    """PIP 패키지 관리 명령어"""
    
    def list(self):
        """pip 패키지 목록 조회"""
        if not self._validate_project_path():
            return
        
        requirements_path = "requirements.txt"
        if self.fs.exists(requirements_path):
            print("requirements.txt:")
            content = self.fs.read(requirements_path)
            print(content)
        else:
            print("requirements.txt not found.")
            print("\nInstalled packages:")
            os.system("pip list")
    
    def install(self, package=None, version=None):
        """pip 패키지 설치"""
        if not self._validate_project_path():
            return
        
        if package is None:
            # requirements.txt에서 설치
            if self.fs.exists("requirements.txt"):
                print("Installing from requirements.txt...")
                os.system("pip install -r requirements.txt")
            else:
                print("Package name or requirements.txt is required.")
            return
        
        pkg_spec = package
        if version:
            pkg_spec = f"{package}=={version}"
        
        print(f"Installing pip package '{pkg_spec}'...")
        os.system(f"pip install \"{pkg_spec}\"")
        print(f"Package '{pkg_spec}' installed successfully.")
    
    def uninstall(self, package=None):
        """pip 패키지 제거"""
        if not self._validate_project_path():
            return
        
        if package is None:
            print("Package name is required. (--package=dizest)")
            return
        
        print(f"Uninstalling pip package '{package}'...")
        os.system(f"pip uninstall -y {package}")
        print(f"Package '{package}' uninstalled successfully.")
    
    def export(self, output="requirements.txt"):
        """pip 패키지 목록 내보내기 (requirements.txt 생성)"""
        if not self._validate_project_path():
            return
        
        print(f"Exporting pip packages to '{output}'...")
        os.system(f"pip freeze > {output}")
        print(f"Packages exported to '{output}'.")
    
    def import_(self, input_file="requirements.txt"):
        """pip 패키지 가져오기 (requirements.txt에서 설치)"""
        if not self._validate_project_path():
            return
        
        if not self.fs.exists(input_file):
            print(f"File '{input_file}' not found.")
            return
        
        print(f"Importing pip packages from '{input_file}'...")
        os.system(f"pip install -r {input_file}")
        print("Packages imported successfully.")
    
    # import는 예약어이므로 별도 메서드로 우회
    def __getattribute__(self, name):
        if name == 'import':
            return object.__getattribute__(self, 'import_')
        return object.__getattribute__(self, name)
