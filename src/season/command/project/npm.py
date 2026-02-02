import os
import json
import subprocess
from .base import BaseCommand


class NpmCommand(BaseCommand):
    """NPM package management commands (based on project/build folder)"""
    
    def _get_build_path(self, project="main"):
        """Return the build folder path for the project"""
        return os.path.join(self._get_project_path(project), "build")
    
    def _get_angular_package_path(self, project="main"):
        """Return the src/angular/package.json path for the project"""
        return os.path.join(self._get_project_path(project), "src", "angular", "package.json")
    
    def _sync_package_json(self, project="main"):
        """Sync build/package.json to src/angular/package.json"""
        build_package = os.path.join(self._get_build_path(project), "package.json")
        angular_package = self._get_angular_package_path(project)
        
        if self.fs.exists(build_package):
            self.fs.copy(build_package, angular_package)
            print(f"Synced package.json to src/angular/package.json")
    
    def _run_npm_command(self, cmd, project="main"):
        """Execute npm command and return result"""
        build_path = self.fs.abspath(self._get_build_path(project))
        full_cmd = f"cd {build_path} && {cmd}"
        
        p = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        
        result = ""
        if out and len(out) > 0:
            result += out.decode('utf-8').strip()
        if err and len(err) > 0:
            if result:
                result += "\n"
            result += err.decode('utf-8').strip()
        
        return result, p.returncode
    
    def list(self, project="main"):
        """List npm packages (based on src/angular/package.json)"""
        if not self._validate_project_path():
            return
        
        angular_package = self._get_angular_package_path(project)
        if not self.fs.exists(angular_package):
            print(f"package.json not found at '{angular_package}'.")
            return
        
        try:
            content = self.fs.read(angular_package)
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
    
    def install(self, package=None, project="main", version=None, dev=False):
        """Install npm package (runs in build folder and syncs to src/angular)"""
        if not self._validate_project_path():
            return
        
        build_path = self._get_build_path(project)
        print(build_path)
        if not self.fs.isdir(build_path):
            print(f"Build folder not found at '{build_path}'. Run 'wiz project build' first.")
            return
        
        if package is None:
            print("Installing all npm dependencies...")
            result, code = self._run_npm_command("npm install", project)
            print(result)
            return
        
        pkg_spec = package
        if version:
            pkg_spec = f"{package}@{version}"
        
        save_flag = "--save-dev" if dev else "--save"
        print(f"Installing npm package '{pkg_spec}'...")
        
        result, code = self._run_npm_command(f"npm install {save_flag} {pkg_spec}", project)
        print(result)
        
        if code == 0:
            self._sync_package_json(project)
            print(f"Package '{pkg_spec}' installed successfully.")
        else:
            print(f"Failed to install package '{pkg_spec}'.")
    
    def uninstall(self, package=None, project="main"):
        """Uninstall npm package (runs in build folder and syncs to src/angular)"""
        if not self._validate_project_path():
            return
        
        if package is None:
            print("Package name is required. (--package=@angular/core)")
            return
        
        build_path = self._get_build_path(project)
        if not self.fs.isdir(build_path):
            print(f"Build folder not found at '{build_path}'. Run 'wiz project build' first.")
            return
        
        print(f"Uninstalling npm package '{package}'...")
        
        result, code = self._run_npm_command(f"npm uninstall --save {package}", project)
        print(result)
        
        if code == 0:
            self._sync_package_json(project)
            print(f"Package '{package}' uninstalled successfully.")
        else:
            print(f"Failed to uninstall package '{package}'.")
