import season
import os

class BaseCommand:
    """프로젝트 명령어 기본 클래스"""
    
    # wiz 프로젝트 확인에 필요한 설정 파일들
    WIZ_CONFIG_FILES = ["config/boot.py", "config/ide.py", "config/service.py"]
    
    def __init__(self):
        self.wiz_root = self._find_wiz_root()
        self.fs = season.util.fs(self.wiz_root) if self.wiz_root else season.util.fs(os.getcwd())
        self.project_base = "project"
        self.portal_base = "portal"
    
    def _is_wiz_project(self, path):
        """주어진 경로가 wiz 프로젝트인지 확인"""
        for config_file in self.WIZ_CONFIG_FILES:
            if not os.path.isfile(os.path.join(path, config_file)):
                return False
        return True
    
    def _find_wiz_root(self):
        """
        현재 디렉토리부터 부모 디렉토리를 재귀적으로 탐색하여 wiz 프로젝트 루트를 찾음
        config/boot.py, config/ide.py, config/service.py 파일이 모두 존재하는 디렉토리를 찾음
        심볼릭 링크인 경우 심볼릭 링크 경로를 유지함
        """
        # PWD 환경 변수를 사용하여 심볼릭 링크 경로 유지
        current_path = os.environ.get('PWD', os.getcwd())
        
        while True:
            if self._is_wiz_project(current_path):
                return current_path
            
            parent_path = os.path.dirname(current_path)
            
            # 루트 디렉토리에 도달하면 종료
            if parent_path == current_path:
                return None
            
            current_path = parent_path
        
        return None
    
    def _get_wiz_root(self):
        """wiz 프로젝트 루트 경로 반환"""
        return self.wiz_root
    
    def _validate_project_path(self):
        """wiz 프로젝트 경로 유효성 검사"""
        if self.wiz_root is None:
            print("Invalid Project path: wiz structure not found. Looking for config/boot.py, config/ide.py, config/service.py")
            return False
        return True
    
    def _get_project_path(self, project_name):
        """프로젝트 경로 반환"""
        return os.path.join(self.project_base, project_name)
    
    def _get_portal_path(self, project="main", package_name=None):
        """포탈 패키지 경로 반환"""
        return os.path.join(self._get_project_path(project), "src", "portal", package_name)
    
    def _get_app_base_path(self, project="main", package=None):
        """앱 기본 경로 반환 (package 옵션에 따라 src/app 또는 portal/<package>/app)"""
        if package:
            return os.path.join(self._get_project_path(project), "src", "portal", package, "app")
        return os.path.join(self._get_project_path(project), "src", "app")
    
    def _get_controller_base_path(self, project="main", package=None):
        """컨트롤러 기본 경로 반환"""
        if package:
            return os.path.join(self._get_project_path(project), "src", "portal", package, "controller")
        return os.path.join(self._get_project_path(project), "src", "controller")
    
    def _get_model_base_path(self, project="main", package=None):
        """모델 기본 경로 반환"""
        if package:
            return os.path.join(self._get_project_path(project), "src", "portal", package, "model")
        return os.path.join(self._get_project_path(project), "src", "model")
    
    def _get_route_base_path(self, project="main", package=None):
        """라우트 기본 경로 반환"""
        if package:
            return os.path.join(self._get_project_path(project), "src", "portal", package, "route")
        return os.path.join(self._get_project_path(project), "src", "route")
    
    def _namespace_to_path(self, namespace):
        """네임스페이스를 경로로 변환"""
        return namespace
    
    def help(self):
        """도움말 출력"""
        print("Available actions:")
        for method_name in dir(self):
            if not method_name.startswith('_') and method_name != 'help':
                method = getattr(self, method_name)
                if callable(method):
                    doc = method.__doc__ or ""
                    print(f"  {method_name}: {doc.strip()}")
