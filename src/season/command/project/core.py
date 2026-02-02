import season
import os
from .base import BaseCommand


class ProjectCommand(BaseCommand):
    """프로젝트 기본 명령어"""
    
    def build(self, project="main", clean=False):
        """프로젝트 빌드"""
        if not self._validate_project_path():
            return
        
        project_path = self._get_project_path(project)
        if not self.fs.isdir(project_path):
            print(f"Project '{project}' does not exist.")
            return
        
        print(f"Building project '{project}'...")
        
        try:
            wiz_root = self._get_wiz_root()
            app = season.server(wiz_root)
            wiz = app.wiz()
            wiz.project(project)
            
            # Update app.json for src/app and src/portal
            print(f"Updating app.json configurations...")
            try:
                Namespace = wiz.ide.plugin("workspace").model("src/build/namespace", mode="context")
                Annotator = wiz.ide.plugin("workspace").model("src/build/annotator", mode="context")
                fs = wiz.project.fs()

                # Update src/app
                if fs.isdir("src/app"):
                    apps = fs.list("src/app")
                    for appid in apps:
                        appjsonpath = os.path.join("src", "app", appid, "app.json")
                        tspath = os.path.join("src", "app", appid, "view.ts")
                        
                        if fs.isfile(appjsonpath) and fs.isfile(tspath):
                            try:
                                tscode = fs.read(tspath, "")
                                appjson = fs.read.json(appjsonpath)
                                appjson['id'] = appid
                                selector = Namespace.selector(appid)
                                cinfo = Annotator.definition.ngComponentDesc(tscode)
                                injector = [f'[{x}]=""' for x in cinfo['inputs']] + [f'({x})=""' for x in cinfo['outputs']]
                                injector = ", ".join(injector)
                                appjson['template'] = selector + "(" + injector + ")"
                                fs.write.json(appjsonpath, appjson)
                            except:
                                pass

                # Update src/portal
                if fs.isdir("src/portal"):
                    modules = fs.list("src/portal")
                    for modname in modules:
                        for type_dir in ['app', 'widget']:
                            base_app_path = os.path.join("src", "portal", modname, type_dir)
                            if fs.isdir(base_app_path):
                                apps = fs.list(base_app_path)
                                for appid in apps:
                                    appjsonpath = os.path.join(base_app_path, appid, "app.json")
                                    tspath = os.path.join(base_app_path, appid, "view.ts")
                                    
                                    if fs.isfile(appjsonpath) and fs.isfile(tspath):
                                        try:
                                            tscode = fs.read(tspath, "")
                                            appjson = fs.read.json(appjsonpath)
                                            appjson['id'] = appid
                                            appjson['type'] = type_dir
                                            app_id = f"portal.{modname}.{appid}"
                                            selector = Namespace.selector(app_id)
                                            cinfo = Annotator.definition.ngComponentDesc(tscode)
                                            injector = [f'[{x}]=""' for x in cinfo['inputs']] + [f'({x})=""' for x in cinfo['outputs']]
                                            injector = ", ".join(injector)
                                            appjson['template'] = selector + "(" + injector + ")"
                                            fs.write.json(appjsonpath, appjson)
                                        except:
                                            pass
            except Exception as e:
                 print(f"Warning: Failed to update app.json: {e}")

            # workspace 플러그인에서 builder 모델 로드
            builder = wiz.ide.plugin("workspace").model("builder", mode="context")
            
            if clean:
                print(f"Cleaning project '{project}' build cache...")
                builder.clean()
            
            builder.build()
                        
            print(f"Project '{project}' build completed.")
        except Exception as e:
            print(f"Build failed: {e}")
            raise e
    
    def create(self, project="demo", uri=None, path=None):
        """프로젝트 생성"""
        if not self._validate_project_path():
            return
        
        project_path = self._get_project_path(project)
        
        if self.fs.isdir(project_path):
            print(f"Project '{project}' already exists.")
            return
        
        print(f"Creating project '{project}'...")
        
        try:
            wiz_root = self._get_wiz_root()
            app = season.server(wiz_root)
            wiz = app.wiz()

            if uri:
                print(f"Cloning from git: {uri}")
                os.system(f"git clone {uri} {project_path}")
            elif path:
                print(f"Copying from path: {path}")
                self.fs.copy(path, project_path)
            else:
                print("Creating default demo project...")
                sample_path = os.path.join(season.PATH_LIB, "data", "sample")
                self.fs.copy(sample_path, project_path)
            
            if not self.fs.exists(project_path):
                print(f"Project '{project}' creation failed.")
                return

            if not self.fs.exists(os.path.join(project_path, "config")):
                self.fs.makedirs(os.path.join(project_path, "config"))

            wiz.project(project)
            
            builder = wiz.ide.plugin("workspace").model("builder", mode="context")
            builder.clean()
            builder.build()
            
            print(f"Project '{project}' created successfully.")
        except Exception as e:
            print(f"Create failed: {e}")
    
    def delete(self, project=None):
        """프로젝트 삭제"""
        if not self._validate_project_path():
            return
        
        if project is None:
            print("Project name is required.")
            return
        
        project_path = self._get_project_path(project)
        
        if not self.fs.isdir(project_path):
            print(f"Project '{project}' does not exist.")
            return
        
        print(f"Deleting project '{project}'...")
        self.fs.remove(project_path)
        print(f"Project '{project}' deleted successfully.")
    
    def list(self):
        """프로젝트 목록 조회"""
        if not self._validate_project_path():
            return
        
        if not self.fs.isdir(self.project_base):
            print("No projects found.")
            return
        
        projects = self.fs.list(self.project_base)
        print("Projects:")
        for p in projects:
            if self.fs.isdir(os.path.join(self.project_base, p)):
                print(f"  - {p}")
    
    def clean(self, project="main"):
        """프로젝트 캐시 정리"""
        if not self._validate_project_path():
            return
        
        print(f"Cleaning project '{project}' cache...")
        cache_path = ".wiz.cache"
        if self.fs.isdir(cache_path):
            self.fs.remove(cache_path)
        print(f"Project '{project}' cache cleaned.")
