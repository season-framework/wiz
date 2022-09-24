import season
import os
import base64
import json
import datetime
import markupsafe
from abc import *
import subprocess

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
    fs.write('esbuild.js', ESBUILD_SCRIPT)

    packagejson = fs.read.json("package.json")
    packagejson["scripts"]["esbuild"] = "node esbuild"
    fs.write.json("package.json", packagejson)

def build_default(workspace, app):
    def build_app(app):
        cmd = f"cd {workspace.build.path()} && node esbuild"
        build_folder = workspace.build.folder()

        appids = app.id.split(".")
        targetfs = workspace.fs(build_folder, "src", "app", *appids)
        srcfs = app.fs()        
        package = app.data(code=False)['package']

        if srcfs.exists():
            filename = appids[-1] + ".component"
            componentname = []
            for wsappname in appids:
                componentname.append(wsappname.capitalize())
            componentname = "".join(componentname)

            if targetfs.isdir() == False:
                targetfs.makedirs()
            targetfs.copy(srcfs.abspath("view.pug"), filename + ".pug")
            targetfs.copy(srcfs.abspath("view.scss"), filename + ".scss")

            # convert customized typescript
            tsfile = srcfs.read("view.ts")
            
            implements = 'OnInit'
            if 'ng.implements' in package:
                implements = package['ng.implements']
            if len(implements) < 3:
                implements = "OnInit"

            importstr = "import { Component, OnInit } from '@angular/core';\n"

            if implements != 'OnInit':
                implementsarr = implements.split(".")
                implementsfilename = implementsarr[-1] + ".component"
                implementscomp = []
                for wsappname in implementsarr:
                    implementscomp.append(wsappname.capitalize())
                implementscomp = "".join(implementscomp) + "Component"
                implementsfrom = "../".join(['' for x in range(len(appids) + 1)]) + "/".join(implements.split(".")) + "/" + implementsfilename
                importstr = f"{importstr}import {implementscomp} from '{implementsfrom}';\n"
            else:
                implementscomp = implements

            tsfile = tsfile.replace('export class Controller', f'export class {componentname}Component implements {implementscomp}')
            
            tsfile = f"{importstr}\n" \
                + "@Component({\n    selector: 'app-" + "-".join(appids) + "',\n    templateUrl: './" + filename + ".html',\n    styleUrls: ['./" + filename + ".scss']\n})\n" \
                + tsfile.strip()

            targetfs.write(filename + ".ts", tsfile)

            target = targetfs.abspath(filename)
            cmd = f"{cmd} {target}"
            build_cmd(workspace, cmd)

            return dict(name=componentname + "Component", path="./" + "/".join(appids) + "/" + filename)
        else:
            targetfs.delete()

    build_folder = workspace.build.folder()

    modules = []
    if app.is_instance():
        item = build_app(app)
        if item is not None:
            modules.append(item)
    else:
        apps = app.list()
        fs = workspace.fs(build_folder, "src", "app")
        for item in fs.list():
            if fs.isdir(item):
                fs.delete(item)

        for pkg in apps:
            app_id = pkg['package']['id']
            _app = app(app_id)
            item = build_app(_app)
            if item is not None:
                modules.append(item)

    
    cmd = f"cd {workspace.build.path()} && node esbuild"
    fs = workspace.fs(build_folder, "src", "app")

    # TODO update: app.component.scss
    # TODO update: app.component.html

    # auto build: app.module.ts
    imports = 'BrowserModule,AppRoutingModule'.split(",")
    app_modules = "import { NgModule } from '@angular/core';\nimport { BrowserModule } from '@angular/platform-browser';\n\n"
    app_modules = app_modules + "import { AppRoutingModule } from './app-routing.module';\nimport { AppComponent } from './app.component';\n\n"
    app_modules = app_modules + "\n".join(["import { " + x['name'] + " } from '" + x['path'] + "';" for x in modules])
    app_modules = app_modules + "\n\n@NgModule({\n  declarations: [\n    AppComponent,\n"
    app_modules = app_modules + ",\n".join(["    " + x['name'] for x in modules])
    app_modules = app_modules + "\n  ],\n  imports: [\n"
    app_modules = app_modules + ",\n".join(["    " + x for x in imports])
    app_modules = app_modules + "\n  ],\n  providers: [],\n  bootstrap: [AppComponent]\n})\nexport class AppModule { }"

    fs.write("app.module.ts", app_modules)
    
    # TODO auto build: app-routing.modules.ts
    
    # run esbuild
    build_cmd(workspace, cmd)

    # copy to dist
    fs = workspace.fs()
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

    # general functions
    def build(self):
        workspace = self.workspace
        workspace.build.init()
        workspace.build(self)

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
    
    def path(self, *args):
        workspace = self.workspace
        wiz = workspace.wiz
        config = wiz.server.config.build
        return workspace.fs(config.folder).abspath()

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
        fs = workspace.fs()
        if fs.exists(config.folder):
            fs.delete(config.folder)
        self.init()
        self()

    def __call__(self, app=None):
        workspace = self.workspace
        wiz = workspace.wiz
        config = wiz.server.config.build

        if app is None:
            app = workspace.app

        fn = build_default
        if config.build is not None:
            fn = config.build

        season.util.fn.call(fn, wiz=wiz, workspace=workspace, season=season, config=config, app=app)

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
