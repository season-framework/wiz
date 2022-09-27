import season
import os
import base64
import json
import datetime
import markupsafe
from abc import *
import subprocess
import time

ESBUILD_SCRIPT = """const fs = require('fs');
const pug = require('pug');

const target = process.argv[2];
if (target) {
    const targetpath = target + '.pug';
    const savepath = target + '.html';
    const compiledFunction = pug.compileFile(targetpath);
    fs.writeFileSync(savepath, compiledFunction(), "utf8")
} else {
    const NgcEsbuild = require('ngc-esbuild');
    new NgcEsbuild({
        minify: true,
        open: false,
        serve: false,
        watch: false
    }).resolve.then((result) => {
        process.exit(1);
    });
}
"""

ENV_SCRIPT = """export const environment = {
  production: true
};"""

def build_cmd(workspace, cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    logger = workspace.wiz.logger('[build]')
    if out is not None and len(out) > 0: workspace.wiz.logger('[build][log]')(out.decode('utf-8').strip())
    if err is not None and len(err) > 0: workspace.wiz.logger('[build][error]')(err.decode('utf-8').strip(), level=season.LOG_CRITICAL)

def build_default_init(workspace, config):
    rootfs = workspace.fs()
    working_dir = rootfs.abspath()
    build_folder = workspace.build.folder()
    build_dir = os.path.join(working_dir, build_folder)

    if rootfs.exists(build_folder):
        return

    build_cmd(workspace, f'cd {working_dir} && {config.command_ng} new {build_folder} --routing true --style scss --interactive false  --skip-tests true --skip-git true > /dev/null')    
    build_cmd(workspace, f'cd {build_dir} && npm install ngc-esbuild pug > /dev/null')
    
    fs = workspace.fs(build_dir)
    fs.write('wizbuild.js', ESBUILD_SCRIPT)
    fs.write(os.path.join('src', 'environments', 'environment.ts'), ENV_SCRIPT)

def build_default(workspace, filepath):
    fs = workspace.fs()
    buildfs = workspace.build.fs()
    build_folder = workspace.build.folder()
    pugfiles = []

    if len(filepath) == 0:
        buildfs.delete("src/app")
        buildfs.delete("src/service")

    # build file and pug cache
    def build_file(target_file):
        target_file_split = target_file.split("/")
        target_folder = ['angular', 'app', '']
        target = target_file_split[0]
        if target not in target_folder:
            return

        if fs.exists(target_file) == False:
            fs.delete(target_file)
            return

        if fs.isdir(target_file):
            files = fs.files(target_file)
            for file in files:
                build_file(os.path.join(target_file, file))
            return
        
        extension = os.path.splitext(target_file)[-1]

        # catch pug files
        if extension == '.pug':
            pugbuildpath = fs.abspath(target_file[:-len(extension)])
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

                code = fs.read(target_file)
                appjson = fs.read.json(os.path.join(os.path.dirname(target_file), "app.json"), dict())
                
                importstr = "import { Component, OnInit } from '@angular/core';\n"
                implements = 'OnInit'
                if 'ng.implements' in appjson:
                    implements = appjson['ng.implements']
                if len(implements) < 3:
                    implements = "OnInit"

                if implements != 'OnInit':
                    implementsarr = implements.split(".")
                    implementsfilename = implementsarr[-1] + ".component"
                    implementscomp = []
                    for wsappname in implementsarr:
                        implementscomp.append(wsappname.capitalize())
                    implementscomp = "".join(implementscomp) + "Component"
                    implementsfrom = "../".join(['' for x in range(len(app_id_split) + 1)]) + implements + "/" + implementsfilename
                    importstr = f"{importstr}import {implementscomp} from '{implementsfrom}';\n"
                else:
                    implementscomp = implements

                code = code.replace("@wiz.service", "src/service")
                code = code.replace("@wiz.app", "src/app")
                code = code.replace('export class Controller', "@Component({\n    selector: 'app-" + "-".join(app_id_split) + "',\n    templateUrl: './view.html',\n    styleUrls: ['./view.scss']\n})\n" + f'export class {componentname}Component implements {implementscomp}')
                code = f"{importstr}\n" + code.strip()

                copyfile = os.path.join(copyfolder, filename + ".ts")                
                buildfs.write(copyfile, code)

                appjson["ng.build"] = dict(id=app_id, name=componentname + "Component", path="./" + app_id + "/" + filename)
                fs.write(os.path.join(os.path.dirname(target_file), "app.json"), json.dumps(appjson, indent=4))
            else:
                buildfs.copy(fs.abspath(target_file), copyfile)
        
        elif target == 'angular':
            ngtarget = target_file_split[1]
            ngfilepath = os.path.join(*target_file.split("/")[1:])

            copyfile = os.path.join("src", ngfilepath)
            copyfolder = os.path.dirname(copyfile)
            if buildfs.isdir(copyfolder) == False:
                buildfs.makedirs(copyfolder)

            if ngtarget == 'service':
                code = fs.read(target_file)
                code = code.replace("export class", "import { Injectable } from '@angular/core';\n@Injectable({ providedIn: 'root' })\nexport class")
                buildfs.write(copyfile, code)
            elif ngtarget in ['app', 'index.html', 'styles.scss']:
                buildfs.copy(fs.abspath(target_file), copyfile)
            elif ngtarget == 'angular.build.options.json':
                ng_build_options = fs.read.json(target_file)
                angularjson = buildfs.read.json("angular.json", dict())
                for key in ng_build_options:
                    if key in ["outputPath", "index", "main", "polyfills", "tsConfig", "inlineStyleLanguage"]: continue
                    angularjson["projects"][build_folder]["architect"]["build"]["options"][key] = ng_build_options[key]
                buildfs.write("angular.json", json.dumps(angularjson, indent=4))

    build_file(filepath)
        
    # compile pug files as bulk
    pugfilepaths = " ".join(pugfiles)
    cmd = f"cd {buildfs.abspath()} && node wizbuild {pugfilepaths}"
    build_cmd(workspace, cmd)

    for pugfile in pugfiles:
        pugfile = pugfile[len(fs.abspath()) + 1:]
        target = pugfile.split("/")[0]
        htmlfile = pugfile + ".html"
        
        if target == 'app':
            copyfile = os.path.join("src", pugfile + ".html")
            copyfolder = os.path.dirname(copyfile)
            if buildfs.isdir(copyfolder) == False:
                buildfs.makedirs(copyfolder)
            buildfs.copy(fs.abspath(htmlfile), copyfile)

        elif htmlfile == 'angular/index.html':
            copyfile = os.path.join("src", "index.html")
            buildfs.copy(fs.abspath(htmlfile), copyfile)

        elif htmlfile == 'angular/app/app.component.html':
            copyfile = os.path.join("src", "app", "app.component.html")
            buildfs.copy(fs.abspath(htmlfile), copyfile)

    # load apps
    apps = workspace.app.list()
    appsmap = dict()
    _apps = []
    for app in apps:
        try:
            _apps.append(app['package']['ng.build'])
            appsmap[app['package']['id']] = app['package']['ng.build']
        except:
            pass
    apps = _apps

    component_import = "\n".join(["import { " + x['name'] + " } from '" + x['path'] + "';" for x in apps])
    component_declarations = "AppComponent,\n" + ",\n".join(["    " + x['name'] for x in apps])
    
    # auto build: app.module.ts
    app_module_ts = fs.read(os.path.join("angular", "app.module.ts"))
    app_module_ts = app_module_ts.replace("WizComponentDeclarations", component_declarations)
    app_module_ts = component_import + "\n\n" + app_module_ts
    buildfs.write(os.path.join("src", "app", "app.module.ts"), app_module_ts)

    # auto build: app-routing.modules.ts
    app_routings = fs.read.json(os.path.join("angular", "routing.json"), [])
    app_routing_json = []
    for app_routing in app_routings:
        if app_routing['app'] not in appsmap:
            continue
        _path = app_routing['path']
        _component = appsmap[app_routing['app']]['name']
        app_routing_json.append("{ path : '" + _path + "', component: " + _component + " }")
    
    app_routing_ts = "import { NgModule } from '@angular/core';\nimport { RouterModule, Routes } from '@angular/router';\n"
    app_routing_ts = app_routing_ts + "\n" + component_import
    app_routing_ts = app_routing_ts + "\n\n" + "const routes: Routes = [\n    " + ",\n    ".join(app_routing_json) + "\n];"
    app_routing_ts = app_routing_ts + "\n\n" + "@NgModule({ imports: [RouterModule.forRoot(routes)], exports: [RouterModule] })"
    app_routing_ts = app_routing_ts + "\n" + "export class AppRoutingModule { }"
    buildfs.write(os.path.join("src", "app", "app-routing.module.ts"), app_routing_ts)

    # run esbuild
    cmd = f"cd {workspace.build.path()} && node wizbuild"
    build_cmd(workspace, cmd)

    # copy to dist
    if fs.isdir("dist"): fs.remove("dist")
    fs.copy(fs.abspath(os.path.join(build_folder, "dist", build_folder)), "dist")

def localized(fn):
    def wrapper_function(self, *args, **kwargs):
        if self.id is None:
            raise Exception("Not Localized Instance")
        return fn(self, *args, **kwargs)
    return wrapper_function

class Route:
    def __init__(self, workspace):
        self.workspace = workspace
        self.wiz = workspace.wiz
        self.id  = None
    
    def list(self):
        fs = self.workspace.fs('route')
        routes = fs.files()
        res = []
        for id in routes:
            route = self(id).data(code=False)
            if route is None:
                continue
            res.append(route)
        res.sort(key=lambda x: x['package']['id'])
        return res

    def is_instance(self):
        return self.id is not None

    def build(self):
        pass

    def __call__(self, id):
        id = id.lower()
        route = Route(self.workspace)
        route.id = id
        return route

    @localized
    def fs(self, *args):
        return self.workspace.fs('route', self.id, *args)

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
        
        def readfile(key, filename, default=""):
            try: 
                pkg[key] = fs.read(filename)
            except: 
                pkg[key] = default
            return pkg
        
        if code:
            pkg = readfile("controller", "controller.py")
            
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

    @localized
    def dic(self, lang=None):
        APP_ID = self.id
        wiz = self.wiz
        fs = self.fs("dic")

        if lang is None:
            lang = wiz.request.language()
            lang = lang.lower()
        
        data = fs.read.json(f'{lang}.json', None)
        if data is None:
            data = fs.read.json("default.json", dict())
        
        class Loader:
            def __init__(self, dicdata):
                self.dicdata = dicdata

            def __call__(self, key=None):
                dicdata = self.dicdata
                if key is None: 
                    return season.util.std.stdClass(dicdata)
                
                key = key.split(".")
                tmp = dicdata
                for k in key:
                    if k not in tmp:
                        return ""
                    tmp = tmp[k]
                return tmp

        return Loader(data)
    
    @localized
    def update(self, data):
        required = ['package', 'dic', 'controller']
        for key in required:
            if key not in data: 
                raise Exception(f"'`{key}`' not defined")

        for key in data:
            if type(data[key]) == str:
                data[key] = data[key].replace('', '')

        data['package']['id'] = self.id

        if len(data['package']['id']) < 3:
            raise Exception(f"id length at least 3")
        
        allowed = "qwertyuiopasdfghjklzxcvbnm.1234567890"
        for c in data['package']['id']:
            if c not in allowed:
                raise Exception(f"only alphabet and number and . in package id")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 'created' not in data['package']:
            data['package']['created'] = timestamp

        viewtype = 'pug'
        if 'viewtype' in data['package']:
            viewtype = data['package']['viewtype']
        if viewtype not in ['pug', 'html']:
            viewtype = 'pug'

        fs = self.fs()
        fs.write.json("app.json", data['package'])
        fs.write("controller.py", data['controller'])
        
        if fs.isdir("dic"):
            fs.delete("dic")
        fs.makedirs("dic")
        dicdata = data['dic']
        for lang in dicdata:
            val = dicdata[lang]
            lang = lang.lower()
            fs.write(os.path.join("dic", lang + ".json"), val)

    @localized
    def delete(self):
        self.fs().delete()
    
class App:
    def __init__(self, workspace):
        self.workspace = workspace
        self.wiz = workspace.wiz
        self.id  = None

    def list(self):
        fs = self.workspace.fs('app')
        apps = fs.files()
        res = []
        for app_id in apps:
            app = self(app_id).data(code=False)
            if app is None:
                continue
            res.append(app)
        res.sort(key=lambda x: x['package']['id'])
        return res

    def is_instance(self):
        return self.id is not None

    def __call__(self, app_id):
        app_id = app_id.lower()
        app = App(self.workspace)
        app.id = app_id
        return app

    # localized functions: app id required
    @localized
    def build(self):
        filepath = None
        if self.is_instance():
            filepath = self.fs().abspath()
        self.workspace.build(filepath)

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

    @localized
    def dic(self, lang=None):
        APP_ID = self.id
        wiz = self.wiz
        fs = self.fs("dic")

        if lang is None:
            lang = wiz.request.language()
            lang = lang.lower()
        
        data = fs.read.json(f'{lang}.json', None)
        if data is None:
            data = fs.read.json("default.json", dict())
        
        class Loader:
            def __init__(self, dicdata):
                self.dicdata = dicdata

            def __call__(self, key=None):
                dicdata = self.dicdata
                if key is None: 
                    return season.util.std.stdClass(dicdata)
                
                key = key.split(".")
                tmp = dicdata
                for k in key:
                    if k not in tmp:
                        return ""
                    tmp = tmp[k]
                return tmp

        return Loader(data)

    @localized
    def api(self):
        APP_ID = self.id
        wiz = self.wiz
        app = self.data()

        if app is None or 'api' not in app:
            return None

        code = app['api']
        if len(code) == 0:
            return None

        ctrl = None
        if 'controller' in app['package'] and len(app['package']['controller']) > 0:
            ctrl = app['package']['controller']
            ctrl = wiz.controller(ctrl)
        
        tag = wiz.mode()
        logger = wiz.logger(f"[{tag}/app/{APP_ID}/api]")
        dic = self.dic()
        name = self.fs().abspath("api.py")
        apifn = season.util.os.compiler(view_api, name=name, logger=logger, controller=ctrl, dic=dic, wiz=wiz)

        return apifn

    @localized
    def update(self, data):
        required = ['package', 'dic', 'api', 'socketio', 'view', 'typescript', 'scss']
        for key in required:
            if key not in data: 
                raise Exception(f"'`{key}`' not defined")

        for key in data:
            if type(data[key]) == str:
                data[key] = data[key].replace('', '')

        data['package']['id'] = self.id

        if len(data['package']['id']) < 3:
            raise Exception(f"id length at least 3")
        
        allowed = "qwertyuiopasdfghjklzxcvbnm.1234567890"
        for c in data['package']['id']:
            if c not in allowed:
                raise Exception(f"only alphabet and number and . in package id")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 'created' not in data['package']:
            data['package']['created'] = timestamp

        viewtype = 'pug'
        if 'viewtype' in data['package']:
            viewtype = data['package']['viewtype']
        if viewtype not in ['pug', 'html']:
            viewtype = 'pug'

        fs = self.fs()
        fs.write.json("app.json", data['package'])
        fs.write("api.py", data['api'])
        fs.write("socketio.py", data['socketio'])
        fs.write(f"view.{viewtype}", data['view'])
        fs.write("view.ts", data['typescript'])
        fs.write("view.scss", data['scss'])
        
        if fs.isdir("dic"):
            fs.delete("dic")
        fs.makedirs("dic")

        dicdata = data['dic']
        for lang in dicdata:
            val = dicdata[lang]
            lang = lang.lower()
            fs.write(os.path.join("dic", lang + ".json"), val)

        self.build()

    @localized
    def delete(self):
        self.fs().delete()
        self.build()

class Build:
    def __init__(self, workspace):
        self.workspace = workspace

    def folder(self):
        workspace = self.workspace
        wiz = workspace.wiz
        config = wiz.server.config.build
        return config.folder
    
    def fs(self, *args):
        return self.workspace.fs(self.folder())

    def path(self, *args):
        return self.fs().abspath()

    def init(self):
        workspace = self.workspace
        wiz = workspace.wiz
        config = wiz.server.config.build

        fn = build_default_init
        if config.init is not None:
            fn = config.init

        season.util.fn.call(fn, wiz=wiz, workspace=workspace, season=season, config=config)

    def clean(self):
        workspace = self.workspace
        wiz = workspace.wiz
        config = wiz.server.config.build
        
        fs = self.fs()
        if fs.exists():
            fs.delete()

        self.init()

    def __call__(self, filepath=None):
        workspace = self.workspace
        wiz = workspace.wiz
        config = wiz.server.config.build

        fn = build_default
        if config.build is not None:
            fn = config.build

        rootpath = workspace.fs().abspath()
        if filepath is None:
            filepath = ""
        elif filepath.startswith(rootpath):
            filepath = filepath[len(rootpath):]
            if len(filepath) > 0 and filepath[0] == "/":
                filepath = filepath[1:]

        season.util.fn.call(fn, wiz=wiz, workspace=workspace, season=season, config=config, filepath=filepath)

class Workspace(metaclass=ABCMeta):
    def __init__(self, wiz):
        self.wiz = wiz
        self.build = Build(self)
        self.app = App(self)

    @abstractmethod
    def path(self, *args):
        pass

    def fs(self, *args):
        return season.util.os.FileSystem(self.path(*args))
