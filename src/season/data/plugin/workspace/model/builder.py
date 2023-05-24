import season
import subprocess
import os
import json
import re
import time

ESBUILD_SCRIPT = """const fs = require('fs');
const pug = require('pug');

if (process.argv.length > 2) {
    for (let i = 2 ; i < process.argv.length ; i++) {
        const target = process.argv[i];
        const targetpath = target + '.pug';
        const savepath = target + '.html';
        const compiledFunction = pug.compileFile(targetpath);
        fs.writeFileSync(savepath, compiledFunction(), "utf8")
    }
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

Compiler = wiz.model("workspace/build/compiler")
Annotation = wiz.model("workspace/build/annotation")
Namespace = wiz.model("workspace/build/namespace")

class Builder:
    def __init__(self, path=None):
        if path is None:
            path = wiz.workspace("service").fs().abspath()
        
        self.PATH_ROOT = path

    def execute(self, cmd):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        
        logger = wiz.logger('[build]')
        if out is not None and len(out) > 0: 
            out = out.decode('utf-8').strip()
            wiz.logger('[build][log]')(out)
        if err is not None and len(err) > 0: 
            err = err.decode('utf-8').strip()
            if "npm WARN" in err or "- Installing packages (npm)" in err:
                wiz.logger('[build][log]')(err, level=season.LOG_WARNING)
            else: 
                wiz.logger('[build][error]')(err, level=season.LOG_CRITICAL)
        
    def use(self, path=None):
        return Builder(path)

    def path(self, *args):
        return os.path.join(self.PATH_ROOT, *args)

    def fs(self, *args):
        return season.util.os.FileSystem(self.path(*args))

    def baseuri(self):
        return wiz.uri.wiz()

    def init(self):
        execute = self.execute
        fs = self.fs()
        working_dir = self.path()
        build_dir = self.path("build")

        if fs.exists("build"):
            return

        execute(f'cd {working_dir} && npm i')
        command_ng = f"{working_dir}/node_modules/@angular/cli/bin/ng.js"

        execute(f'cd {working_dir} && {command_ng} new build --routing true --style scss --interactive false  --skip-tests true --skip-git true')

        fs.write('build/wizbuild.js', ESBUILD_SCRIPT)
        fs.write('build/src/environments/environment.ts', ENV_SCRIPT)
        
        if fs.isfile("src/angular/package.json"):
            packageJson = fs.read.json("src/angular/package.json")
            fs.write.json("build/package.json", packageJson)
            execute(f"cd {build_dir} && npm install --force")
        else:
            execute(f"cd {build_dir} && npm install ngc-esbuild pug jquery socket.io-client --save")

    def clean(self):
        fs = self.fs()
        if fs.exists("build"):
            fs.delete("build")
        self.init()
    
    def build(self):
        execute = self.execute
        fs = self.fs()
        compiler = Compiler(self)

        if fs.exists("config") == False:
            fs.makedirs("config")

        timestamp = int(time.time() * 1000)
        try:
            if fs.exists("build/working"):
                timestampLog = int(fs.read("build/working"))
                if timestamp - timestampLog < 5000:
                    fs.write("build/working", str(timestamp))
                    return
        except:
            return
        
        fs.write("build/working", str(timestamp))

        # clear build src files
        fs.delete("build/src/app")
        fs.delete("build/src/service")
        fs.delete("build/src/styles")
        fs.delete("build/src/libs")
        fs.delete("build/src/portal")

        # remove portal app
        apps = fs.ls("src/app")
        for app in apps:
            if app.split(".")[0] == "portal":
                fs.remove(os.path.join("src/app", app))

        # remove portal route
        apps = fs.ls("src/route")
        for app in apps:
            if app.split(".")[0] == "portal":
                fs.remove(os.path.join("src/route", app))
        
        fs.remove("src/controller/portal")
        fs.remove("src/model/portal")
        fs.remove("src/assets/portal")
        fs.remove("src/angular/libs/portal")
        fs.remove("src/angular/styles/portal")

        # create cache folder
        if fs.exists("cache/src"):
            fs.delete("cache/src")
        fs.copy("src", "cache/src")

        # build portal framework to cache folder
        modules = fs.ls("portal")

        def buildApp(module, mode="app"):
            apps = fs.ls(os.path.join("portal", module, mode))
            for app in apps:
                namespace = f"portal.{module}.{app}"
                srcpath = os.path.join("portal", module, mode, app)
                targetpath = os.path.join("cache/src/app", namespace)
                fs.copy(srcpath, targetpath)
                appjson = fs.read.json(os.path.join(targetpath, "app.json"), dict())
                appjson['id'] = namespace
                appjson['mode'] = 'portal'
                appjson['path'] = os.path.join(srcpath, "app.json")
                if 'controller' in appjson and len(appjson['controller']) > 0:
                    appjson['controller'] = "portal/" + module + "/" + appjson['controller']
                fs.write.json(os.path.join(targetpath, "app.json"), appjson)

        def buildApi(module):
            apps = fs.ls(os.path.join("portal", module, "route"))
            for app in apps:
                namespace = f"portal.{module}.{app}"
                srcpath = fs.abspath(os.path.join("portal", module, "route", app))
                targetpath = os.path.join("cache/src/route", namespace)
                fs.copy(srcpath, targetpath)
                appjson = fs.read.json(os.path.join(targetpath, "app.json"), dict())
                appjson['id'] = namespace
                if 'controller' in appjson and len(appjson['controller']) > 0:
                    appjson['controller'] = "portal/" + module + "/" + appjson['controller']
                fs.write.json(os.path.join(targetpath, "app.json"), appjson)

        def buildFiles(module, target, src):
            fs.makedirs(os.path.join("cache", "src", src, "portal", module))
            files = fs.ls(os.path.join("portal", module, target))
            for f in files:
                fs.copy(fs.abspath(os.path.join("portal", module, target, f)), os.path.join("cache", "src", src, "portal", module, f))

        for module in modules:
            info = fs.read.json(os.path.join("portal", module, "portal.json"), dict())
            def checker(name):
                if f"use_{name}" in info:
                    return info[f"use_{name}"]
                return False
            
            if checker("app"): buildApp(module)
            if checker("widget"): buildApp(module, mode="widget")
            if checker("route"): buildApi(module)
            if checker("controller"): buildFiles(module, "controller", "controller")
            if checker("model"): buildFiles(module, "model", "model")
            if checker("assets"): buildFiles(module, "assets", "assets")
            if checker("libs"): buildFiles(module, "libs", "angular/libs")
            if checker("styles"): buildFiles(module, "styles", "angular/styles")

        # file search function
        def searchFiles(target_file, result=[], extension=None):
            if fs.isdir(target_file):
                files = fs.files(target_file)
                for f in files:
                    searchFiles(os.path.join(target_file, f), result=result, extension=extension)
                return result
            
            if extension is None:
                result.append(target_file)
                return result

            if os.path.splitext(target_file)[-1] == extension:
                result.append(os.path.join(*os.path.splitext(target_file)[:-1]))
                return result
            
            return result

        # build pug files
        pugs = searchFiles("cache/src", result=[], extension=".pug")
        if len(pugs) > 0:
            pugs = " ".join(pugs)
            build_base_path = fs.abspath()
            execute(f"cd {build_base_path} && node build/wizbuild {pugs}")

        # copy src files to build
        targetfiles = searchFiles("cache/src", result=[])
        for targetfile in targetfiles:
            compiler.source(targetfile)
        
        # angular build automation: app.module.ts, app-routing.module.ts
        apps = fs.ls("cache/src/app")
        _appsmap = dict()
        _apps = []
        apps_routing = dict()
        for app in apps:
            appinfo = fs.read.json(os.path.join("cache/src/app", app, "app.json"))    
            try:
                _apps.append(appinfo['ng.build'])
                _appsmap[appinfo['id']] = appinfo['ng.build']
            except Exception as e:
                pass
            try:
                if appinfo['mode'] == 'page':
                    if appinfo['layout'] not in apps_routing:
                        apps_routing[appinfo['layout']] = []
                    if len(appinfo['viewuri']) > 0:
                        routing_uri = appinfo['viewuri']
                        if routing_uri[0] == "/":
                            routing_uri = routing_uri[1:]
                        apps_routing[appinfo['layout']].append(dict(path=routing_uri, component=appinfo['id'], app_id=appinfo['id']))
            except Exception as e:
                pass
        apps = _apps

        prefix = [dict(name=x['name'], path=x['path']) for x in apps]
        ngmodule_imports = []
        ngmodule_declarations = [x['name'] for x in apps]

        apps = fs.ls("cache/src/app")
        for app in apps:
            if fs.exists(os.path.join("cache/src/app", app, "view.ts")):
                text = fs.read(os.path.join("cache/src/app", app, "view.ts"))

                deps = Annotation.definition.dependencies(text)
                for dep in deps:
                    pkg = deps[dep]
                    tmp = dict(name=dep, path=pkg)
                    if tmp not in prefix:
                        prefix.append(tmp)
                    if dep not in ngmodule_imports:
                        ngmodule_imports.append(dep)

                deps = Annotation.definition.directives(text)
                for dep in deps:
                    pkg = deps[dep]
                    tmp = dict(name=dep, path=pkg)
                    if tmp not in prefix:
                        prefix.append(tmp)
                    if dep not in ngmodule_declarations:
                        ngmodule_declarations.append(dep)
                    
        prefix = "\n".join(["import { " + x['name'] + " } from '" + x['path'] + "';" for x in prefix])
        ngmodule_imports = ",\n".join(["        " + x for x in ngmodule_imports])
        ngmodule_declarations = "AppComponent,\n" + ",\n".join(["        " + x for x in ngmodule_declarations])
        
        # auto build: app.module.ts
        filepath = "build/src/app/app.module.ts"
        compiler.typescript(filepath, declarations=ngmodule_declarations, imports=ngmodule_imports, prefix=prefix)

        # auto build: app-routing.modules.ts        
        def syntax_route(code):
            def convert(match_obj):
                val = match_obj.group(1)
                return 'component: ' + Namespace.componentName(val) + "Component"
            pattern = r"component.*:.*'(.*)'"
            code = re.sub(pattern, convert, code)
            pattern = r'component.*:.*"(.*)"'
            code = re.sub(pattern, convert, code)
            code = code.replace("'component", "component")
            code = code.replace('"component', "component")
            return code

        app_routing_auto = [] 
        for layout in apps_routing:
            children = []
            for child in apps_routing[layout]:
                children.append(child)
            app_routing_auto.append(dict(component=layout, children=children))

        app_routing_auto = json.dumps(app_routing_auto, indent=4)
        app_routing_auto = syntax_route(app_routing_auto)

        filepath = "build/src/app/app-routing.module.ts"
        compiler.typescript(filepath, declarations=ngmodule_declarations, imports=ngmodule_imports, prefix=prefix, fnWizRoutes=app_routing_auto)

        fs.copy(fs.abspath("build/package.json"), "src/angular/package.json")
        fs.copy(fs.abspath("build/angular.json"), "src/angular/angular.json")

        # run esbuild
        esbuildpath = fs.abspath('build')
        execute(f"cd {esbuildpath} && node wizbuild")

        wiz.workspace("service").route.build()

        # create bundle
        fs.remove("bundle")
        fs.makedirs("bundle")
        fs.copy("build/dist/build", "bundle/www")
        fs.copy("cache/src/assets", "bundle/src/assets")
        fs.copy("cache/src/controller", "bundle/src/controller")
        fs.copy("cache/src/model", "bundle/src/model")
        fs.copy("cache/src/route", "bundle/src/route")
        fs.copy("cache/urlmap", "bundle/urlmap")
        fs.copy("config", "bundle/config")

        appfiles = searchFiles("cache/src/app", result=[])

        for appfile in appfiles:
            if os.path.splitext(appfile)[-1] not in ['.py', '.json']:
                continue
            bundlefile = os.path.join("bundle", "/".join(appfile.split("/")[1:]))
            bundlefolder = os.path.dirname(bundlefile)
            fs.makedirs(bundlefolder)
            fs.copy(appfile, bundlefile)

        if fs.exists("build/working"):
            timestampLog = int(fs.read("build/working"))
            fs.remove("build/working")
            if timestamp < timestampLog:
                self.build()

Model = Builder()