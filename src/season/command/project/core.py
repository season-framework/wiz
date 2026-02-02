import season
import os
import zipfile
import subprocess
import datetime
import time
from .base import BaseCommand


class ProjectCommand(BaseCommand):
    """Project core commands"""
    
    def build(self, project="main", clean=False):
        """Build project"""
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

            # Load builder model from workspace plugin
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
        """Create project"""
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
                # Extract if .wizproject file
                if path.endswith('.wizproject'):
                    if not os.path.isfile(path):
                        print(f"File '{path}' not found.")
                        return
                    
                    print(f"Extracting from .wizproject: {path}")
                    self.fs.makedirs(project_path)
                    abs_project_path = self.fs.abspath(project_path)
                    
                    try:
                        with zipfile.ZipFile(path, 'r') as zipdata:
                            zipdata.extractall(abs_project_path)
                        print(f"Extracted to '{project_path}'")
                        
                        # Run pip install if requirements.txt exists
                        requirements_path = os.path.join(abs_project_path, "requirements.txt")
                        if os.path.isfile(requirements_path):
                            print("Installing Python dependencies from requirements.txt...")
                            result = subprocess.run(
                                f"pip install -r {requirements_path}",
                                shell=True,
                                capture_output=True,
                                text=True
                            )
                            if result.returncode == 0:
                                print("Python dependencies installed successfully.")
                            else:
                                print(f"Warning: pip install failed: {result.stderr}")
                    except Exception as e:
                        print(f"Failed to extract .wizproject: {e}")
                        return
                else:
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
        """Delete project"""
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
        """List projects"""
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
        """Clean project cache"""
        if not self._validate_project_path():
            return
        
        print(f"Cleaning project '{project}' cache...")
        cache_path = ".wiz.cache"
        if self.fs.isdir(cache_path):
            self.fs.remove(cache_path)
        print(f"Project '{project}' cache cleaned.")
    
    def export(self, project="main", output=None):
        """Export project as .wizproject file"""
        if not self._validate_project_path():
            return
        
        project_path = self._get_project_path(project)
        if not self.fs.isdir(project_path):
            print(f"Project '{project}' does not exist.")
            return
        
        # Set output filename
        if output is None:
            output = f"{project}.wizproject"
        elif not output.endswith('.wizproject'):
            output = f"{output}.wizproject"
        
        abs_project_path = self.fs.abspath(project_path)
        
        print(f"Exporting project '{project}'...")
        
        # Generate requirements.txt
        requirements_path = os.path.join(abs_project_path, "requirements.txt")
        print("Generating requirements.txt...")
        try:
            p = subprocess.Popen("pip freeze", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if out:
                with open(requirements_path, 'w') as f:
                    f.write(out.decode('utf-8'))
                print(f"requirements.txt created at project root.")
        except Exception as e:
            print(f"Warning: Failed to generate requirements.txt: {e}")
        
        # Create zip file
        print(f"Creating {output}...")
        
        # Folders to include
        contains = ["src", "portal", "config", ".git"]
        # Root files to include
        root_files = ["requirements.txt", "package.json"]
        
        try:
            with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipdata:
                for folder, subfolders, files in os.walk(abs_project_path):
                    # Check if folder should be included
                    check = False
                    for contain in contains:
                        contain_path = os.path.join(abs_project_path, contain)
                        if folder.startswith(contain_path) or folder == abs_project_path:
                            check = True
                            break
                    
                    if folder == abs_project_path:
                        check = True
                    
                    if not check:
                        continue
                    
                    for file in files:
                        file_path = os.path.join(folder, file)
                        rel_path = os.path.relpath(file_path, abs_project_path)
                        
                        # Include only specified files from root, or files from specified folders
                        if folder == abs_project_path:
                            if file in root_files:
                                zipdata.write(file_path, rel_path)
                        else:
                            # Check if file is in specified folder
                            for contain in contains:
                                if rel_path.startswith(contain):
                                    zipdata.write(file_path, rel_path)
                                    break
            
            print(f"Project '{project}' exported to '{output}' successfully.")
        except Exception as e:
            print(f"Export failed: {e}")
