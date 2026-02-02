import season
import os

class BaseCommand:
    """Project command base class"""
    
    # Config files required for wiz project validation
    WIZ_CONFIG_FILES = ["config/boot.py", "config/ide.py", "config/service.py"]
    
    def __init__(self):
        self.wiz_root = self._find_wiz_root()
        self.fs = season.util.fs(self.wiz_root) if self.wiz_root else season.util.fs(os.getcwd())
        self.project_base = "project"
        self.portal_base = "portal"
    
    def _is_wiz_project(self, path):
        """Check if given path is a wiz project"""
        for config_file in self.WIZ_CONFIG_FILES:
            if not os.path.isfile(os.path.join(path, config_file)):
                return False
        return True
    
    def _find_wiz_root(self):
        """
        Recursively search from current directory to parent directories to find wiz project root.
        Looks for directories containing config/boot.py, config/ide.py, config/service.py.
        Preserves symbolic link paths if applicable.
        """
        # Use PWD environment variable to preserve symbolic link path
        current_path = os.environ.get('PWD', os.getcwd())
        
        while True:
            if self._is_wiz_project(current_path):
                return current_path
            
            parent_path = os.path.dirname(current_path)
            
            # Exit when root directory is reached
            if parent_path == current_path:
                return None
            
            current_path = parent_path
        
        return None
    
    def _get_wiz_root(self):
        """Return wiz project root path"""
        return self.wiz_root
    
    def _validate_project_path(self):
        """Validate wiz project path"""
        if self.wiz_root is None:
            print("Invalid Project path: wiz structure not found. Looking for config/boot.py, config/ide.py, config/service.py")
            return False
        return True
    
    def _get_project_path(self, project_name):
        """Return project path"""
        return os.path.join(self.project_base, project_name)
    
    def _get_portal_path(self, project="main", package_name=None):
        """Return portal package path"""
        return os.path.join(self._get_project_path(project), "src", "portal", package_name)
    
    def _get_app_base_path(self, project="main", package=None):
        """Return app base path (src/app or portal/<package>/app based on package option)"""
        if package:
            return os.path.join(self._get_project_path(project), "src", "portal", package, "app")
        return os.path.join(self._get_project_path(project), "src", "app")
    
    def _get_controller_base_path(self, project="main", package=None):
        """Return controller base path"""
        if package:
            return os.path.join(self._get_project_path(project), "src", "portal", package, "controller")
        return os.path.join(self._get_project_path(project), "src", "controller")
    
    def _get_model_base_path(self, project="main", package=None):
        """Return model base path"""
        if package:
            return os.path.join(self._get_project_path(project), "src", "portal", package, "model")
        return os.path.join(self._get_project_path(project), "src", "model")
    
    def _get_route_base_path(self, project="main", package=None):
        """Return route base path"""
        if package:
            return os.path.join(self._get_project_path(project), "src", "portal", package, "route")
        return os.path.join(self._get_project_path(project), "src", "route")
    
    def _namespace_to_path(self, namespace):
        """Convert namespace to path"""
        return namespace
    
    def help(self):
        """Show help"""
        print("Available actions:")
        for method_name in dir(self):
            if not method_name.startswith('_') and method_name != 'help':
                method = getattr(self, method_name)
                if callable(method):
                    doc = method.__doc__ or ""
                    print(f"  {method_name}: {doc.strip()}")
