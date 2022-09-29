from season.core.component.base.workspace import Workspace as Base, App as AppBase
from season.core.component.base.workspace import build_cmd, localized, ESBUILD_SCRIPT, ENV_SCRIPT

import season
import os
import json
import datetime
import subprocess
import re

def build_default_init(workspace, config):
    rootfs = workspace.fs()
    srcfs = workspace.fs("src")

    working_dir = rootfs.abspath()
    build_folder = workspace.build.folder()
    build_dir = os.path.join(working_dir, build_folder)

    if rootfs.exists(build_folder):
        return

    build_cmd(workspace, f'cd {working_dir} && {config.command_ng} new {build_folder} --routing true --style scss --interactive false  --skip-tests true --skip-git true')    
    
    fs = workspace.fs(build_dir)
    fs.write('wizbuild.js', ESBUILD_SCRIPT)
    fs.write(os.path.join('src', 'environments', 'environment.ts'), ENV_SCRIPT)

    if srcfs.isfile(os.path.join("angular", "package.json")):
        fs.copy(srcfs.abspath(os.path.join("angular", "package.json")), "package.json")
        build_cmd(workspace, f"cd {build_dir} && npm install")

    build_cmd(workspace, f"cd {build_dir} && npm install ngc-esbuild pug jquery socket.io-client --save")

def build_default(workspace, filepath):
    def convert_to_class(value):
        app_id_split = value.split(".")
        componentname = []
        for wsappname in app_id_split:
            componentname.append(wsappname.capitalize())
        componentname = "".join(componentname)
        return componentname

    srcfs = workspace.fs()
    distfs = workspace.fs("dist")
    buildfs = workspace.build.fs()
    build_folder = workspace.build.folder()
    pugfiles = []
    
    if len(filepath) == 0:
        buildfs.delete("src/app")

    def replace_import_app(value):
        pattern = r'@wiz.app\((\S+)\)'
        def convert(match_obj):
            val = match_obj.group(1)
            return f'src/app/{val}/{val}.component'
        return re.sub(pattern, convert, value)

    # build file and pug cache
    def build_file(target_file):
        target_file_split = target_file.split("/")
        target_folder = ['angular', 'app', '']
        target = target_file_split[0]
        if target not in target_folder:
            return

        if srcfs.exists(target_file) == False:
            srcfs.delete(target_file)
            return

        if srcfs.isdir(target_file):
            files = srcfs.files(target_file)
            for file in files:
                build_file(os.path.join(target_file, file))
            return
        
        extension = os.path.splitext(target_file)[-1]

        # catch pug files
        if extension == '.pug':
            pugbuildpath = srcfs.abspath(target_file[:-len(extension)])
            pugfiles.append(pugbuildpath)
            return

        # if app src
        if target == 'app':
            copyfile = os.path.join("src", target_file)
            copyfolder = os.path.dirname(copyfile)
            if buildfs.isdir(copyfolder) == False:
                buildfs.makedirs(copyfolder)

            if extension == ".ts":
                app_id = target_file_split[1]
                app_id_split = app_id.split(".")

                filename = app_id + ".component"

                componentname = []
                for wsappname in app_id_split:
                    componentname.append(wsappname.capitalize())
                componentname = "".join(componentname)

                code = srcfs.read(target_file)
                appjson = srcfs.read.json(os.path.join(os.path.dirname(target_file), "app.json"), dict())
                
                importstr = "import { Component, OnInit } from '@angular/core';\n"
                implements = 'OnInit'
                implementscomp = implements

                code = replace_import_app(code)
                code = code.replace('export class Component', "@Component({\n    selector: 'wiz-" + "-".join(app_id_split) + "',\n    templateUrl: './view.html',\n    styleUrls: ['./view.scss']\n})\n" + f'export class {componentname}Component implements {implementscomp}')
                code = f"{importstr}\n" + code.strip()

                wizts = srcfs.read(os.path.join("angular", "wiz.ts")).replace("@wiz.namespace", app_id)
                wizts = wizts.replace("@wiz.baseuri", workspace.wiz.server.config.service.wizurl)
                code = wizts + code

                copyfile = os.path.join(copyfolder, filename + ".ts")                
                buildfs.write(copyfile, code)

                appjson["ng.build"] = dict(id=app_id, name=componentname + "Component", path="./" + app_id + "/" + filename)
                srcfs.write(os.path.join(os.path.dirname(target_file), "app.json"), json.dumps(appjson, indent=4))
            else:
                buildfs.copy(srcfs.abspath(target_file), copyfile)
        
        elif target == 'angular':
            ngtarget = target_file_split[1]
            ngfilepath = os.path.join(*target_file.split("/")[1:])

            copyfile = os.path.join("src", ngfilepath)
            copyfolder = os.path.dirname(copyfile)
            if buildfs.isdir(copyfolder) == False:
                buildfs.makedirs(copyfolder)

            if ngtarget == 'styles':
                ngfilepath = os.path.join(*target_file.split("/")[2:])
                copyfile = os.path.join("src", ngfilepath)
                buildfs.write(copyfile, srcfs.read(target_file))

            elif ngtarget == 'angular.build.options.json':
                ng_build_options = srcfs.read.json(target_file)
                angularjson = buildfs.read.json("angular.json", dict())
                for key in ng_build_options:
                    if key in ["outputPath", "index", "main", "polyfills", "tsConfig", "inlineStyleLanguage"]: continue
                    angularjson["projects"][build_folder]["architect"]["build"]["options"][key] = ng_build_options[key]
                buildfs.write("angular.json", json.dumps(angularjson, indent=4))

            elif ngtarget == 'app' and ngfilepath == 'app/app.component.ts':
                code = srcfs.read(target_file)
                code = replace_import_app(code)
                buildfs.write(copyfile, code)

            elif ngtarget in ['app', 'index.html']:
                buildfs.copy(srcfs.abspath(target_file), copyfile)

    build_file(filepath)
        
    # compile pug files as bulk
    pugfilepaths = " ".join(pugfiles)
    cmd = f"cd {buildfs.abspath()} && node wizbuild {pugfilepaths}"
    build_cmd(workspace, cmd)

    for pugfile in pugfiles:
        pugfile = pugfile[len(srcfs.abspath()) + 1:]
        target = pugfile.split("/")[0]
        htmlfile = pugfile + ".html"
        
        if target == 'app':
            copyfile = os.path.join("src", pugfile + ".html")
            copyfolder = os.path.dirname(copyfile)
            if buildfs.isdir(copyfolder) == False:
                buildfs.makedirs(copyfolder)
            buildfs.copy(srcfs.abspath(htmlfile), copyfile)

        elif htmlfile == 'angular/index.html':
            copyfile = os.path.join("src", "index.html")
            text = srcfs.read(htmlfile).replace("@wiz.baseuri", workspace.wiz.server.config.service.wizurl)
            buildfs.write(copyfile, text)

        elif htmlfile == 'angular/app/app.component.html':
            copyfile = os.path.join("src", "app", "app.component.html")
            buildfs.copy(srcfs.abspath(htmlfile), copyfile)

    # load apps
    apps = workspace.app.list()
    appsmap = dict()
    _apps = []
    for app in apps:
        try:
            _apps.append(app['ng.build'])
            appsmap[app['id']] = app['ng.build']
        except Exception as e:
            pass
    apps = _apps

    component_import = "\n".join(["import { " + x['name'] + " } from '" + x['path'] + "';" for x in apps])
    component_declarations = "AppComponent,\n" + ",\n".join(["        " + x['name'] for x in apps])
    
    # auto build: app.module.ts
    app_module_ts = srcfs.read(os.path.join("angular", "app", "app.module.ts"))
    app_module_ts = app_module_ts.replace("'@wiz.declarations'", component_declarations).replace('"@wiz.declarations"', component_declarations)
    app_module_ts = component_import + "\n\n" + app_module_ts
    buildfs.write(os.path.join("src", "app", "app.module.ts"), app_module_ts)

    # run esbuild
    cmd = f"cd {workspace.build.path()} && node wizbuild"
    build_cmd(workspace, cmd)

    # copy to dist
    if distfs.isdir(): distfs.delete()
    srcfs.copy(buildfs.abspath(os.path.join("dist", build_folder)), distfs.abspath())
    srcfs.copy(buildfs.abspath("package.json"), os.path.join("angular", "package.json"))

class Build:
    def __init__(self, workspace):
        self.workspace = workspace

    def folder(self):
        return "build"
    
    def fs(self, *args):
        return self.workspace.fs(self.folder())

    def path(self, *args):
        return self.fs().abspath()

    def init(self):
        workspace = self.workspace
        wiz = workspace.wiz
        fn = build_default_init
        season.util.fn.call(fn, wiz=wiz, workspace=workspace, season=season, config=wiz.server.config.build)

    def clean(self):
        workspace = self.workspace
        wiz = workspace.wiz
        fs = self.fs()
        if fs.exists():
            fs.delete()
        self.init()

    def __call__(self, filepath=None):
        workspace = self.workspace
        wiz = workspace.wiz
        fn = build_default
        srcfs = workspace.fs().abspath()
        if filepath is None:
            filepath = ""
        elif filepath.startswith(srcfs):
            filepath = filepath[len(srcfs):]
            if len(filepath) > 0 and filepath[0] == "/":
                filepath = filepath[1:]

        season.util.fn.call(fn, wiz=wiz, workspace=workspace, season=season, filepath=filepath, config=wiz.server.config.build)

class App(AppBase):
    def __init__(self, workspace):
        super().__init__(workspace)

    def __call__(self, app_id):
        if app_id is None: return self
        app_id = app_id.lower()
        app = App(self.workspace)
        app.id = app_id
        return app

    def list(self):
        fs = self.workspace.fs('app')
        apps = fs.files()
        res = []
        for app_id in apps:
            app = self(app_id).data(code=False)
            if app is None:
                continue
            res.append(app['package'])
        res.sort(key=lambda x: x['id'])
        return res

    @localized
    def fs(self, *args):
        return self.workspace.fs('app', self.id, *args)

    @localized
    def data(self, code=True):
        APP_ID = self.id
        wiz = self.wiz
        fs = self.fs()

        pkg = dict()
        pkg['package'] = fs.read.json('app.json', None)
        if pkg['package'] is None:
            return None

        pkg['package']['id'] = APP_ID
        
        viewtype = 'pug'
        if 'viewtype' in pkg['package']:
            viewtype = pkg['package']['viewtype']
        if viewtype not in ['pug', 'html']:
            viewtype = 'pug'

        def readfile(key, filename, default=""):
            try: 
                pkg[key] = fs.read(filename)
            except: 
                pkg[key] = default
            return pkg
        
        if code:
            pkg = readfile("api", "api.py")
            pkg = readfile("socketio", "socketio.py")
            pkg = readfile("view", f"view.{viewtype}")
            pkg = readfile("typescript", f"view.ts")
            pkg = readfile("scss", f"view.scss")

            pkg['dic'] = dict()
            if fs.isdir("dic"):
                dics = fs.files("dic")
                for dic in dics:
                    try:
                        lang = os.path.splitext(dic)[0]
                        lang = lang.lower()
                        pkg['dic'][lang] = fs.read(os.path.join("dic", dic), '{}')
                    except:
                        pass

        return pkg

    def before_update(self, data):
        required = ['package', 'dic', 'api', 'socketio', 'view', 'typescript', 'scss']
        for key in required:
            if key not in data: 
                raise Exception(f"'`{key}`' not defined")

        data['package']['id'] = self.id
        if len(data['package']['id']) < 3:
            raise Exception(f"id length at least 3")

        allowed = "qwertyuiopasdfghjklzxcvbnm.1234567890"
        for c in data['package']['id']:
            if c not in allowed:
                raise Exception(f"only alphabet and number and . in package id")

        return data

    def do_update(self, data):
        viewtype = 'pug'
        if 'viewtype' in data['package']:
            viewtype = data['package']['viewtype']
        if viewtype not in ['pug', 'html']:
            viewtype = 'pug'

        fs = self.fs()
        fs.write("api.py", data['api'])
        fs.write("socketio.py", data['socketio'])
        fs.write(f"view.{viewtype}", data['view'])
        fs.write("view.ts", data['typescript'])
        fs.write("view.scss", data['scss'])

class Workspace(Base):
    def __init__(self, wiz):
        super().__init__(wiz)
        self.build = Build(self)
        self.app = App(self)

    def path(self, *args):
        return os.path.join(self.wiz.server.path.ide, *args)
    
    def controller(self, namespace):
        wiz = self.wiz
        fs = self.fs("src", "controller")
        code = fs.read(f"{namespace}.py")
        logger = wiz.logger(f"[ctrl/{namespace}]")
        ctrl = season.util.os.compiler(code, name=fs.abspath(namespace + ".py"), logger=logger, wiz=wiz)
        return ctrl['Controller']
    
    def model(self, namespace):
        wiz = self.wiz
        fs = self.fs("src", "model")
        code = fs.read(f"{namespace}.py")
        logger = wiz.logger(f"[model/{namespace}]")
        model = season.util.os.compiler(code, name=fs.abspath(namespace + ".py"), logger=logger, wiz=wiz)
        return model['Model']
