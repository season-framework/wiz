import season
import os
import json
import re
import time

Code = wiz.ide.plugin.model("src/code")
Util = wiz.ide.plugin.model("src/util")

Annotator = wiz.ide.plugin.model("src/build/annotator")
Namespace = wiz.ide.plugin.model("src/build/namespace")

class Model:
    def __init__(self, path=None):
        if path is None:
            path = wiz.project.fs().abspath()
        self.PATH_ROOT = path

    def fs(self, *args):
        return season.util.filesystem(os.path.join(self.PATH_ROOT, *args))

    def install(self):
        fs = self.fs()
        if fs.exists("build"):
            return
        working_dir = fs.abspath()
        build_dir = fs.abspath("build")

        Util.execute(f'cd {working_dir} && npm i')
        command_ng = f"{working_dir}/node_modules/@angular/cli/bin/ng.js"
        Util.execute(f'cd {working_dir} && {command_ng} new build --routing true --style scss --interactive false --skip-tests true --skip-git true')

        if fs.isfile("src/angular/package.json"):
            packageJson = fs.read.json("src/angular/package.json")
            fs.write.json("build/package.json", packageJson)
            Util.execute(f"cd {build_dir} && npm install --force")
        else:
            Util.execute(f"cd {build_dir} && npm install ngc-esbuild pug jquery socket.io-client --save")

    def __call__(self):
        self.build()

    def clean(self):
        fs = self.fs()
        if fs.exists("build"):
            fs.delete("build")

    def build(self):
        fs = self.fs()
        timestamp = int(time.time() * 1000)
        wiz.server.cache.clear()

        if fs.exists("build"):
            if Util.is_working(fs, timestamp):
                return
        else:
            self.install()
            if Util.is_working(fs, timestamp):
                return

        self._reconstruct()
        self._build()
        self._angular()
        self.bundle()

        wiz.server.cache.clear()
        Route = wiz.ide.plugin.model("route")()
        Route.build()

        if Util.is_work_finish(fs, timestamp) is False:
            self.build()
            return
    
    def bundle(self):
        fs = self.fs()
        fs.remove("bundle")
        fs.makedirs("bundle")

        fs.copy("build/dist/build", "bundle/www")
        fs.copy("build/src/assets", "bundle/src/assets")
        fs.copy("build/src/controller", "bundle/src/controller")
        fs.copy("build/src/model", "bundle/src/model")
        fs.copy("build/src/route", "bundle/src/route")
        fs.copy("config", "bundle/config")

        appfiles = self._search("build/src/app", result=[])

        for appfile in appfiles:
            if os.path.splitext(appfile)[-1] not in ['.py', '.json']:
                continue
            bundlefile = os.path.join("bundle", *appfile.split("/")[1:])
            bundlefolder = os.path.dirname(bundlefile)
            fs.makedirs(bundlefolder)
            fs.copy(appfile, bundlefile)

    def typescript(self, code, app_id=None, baseuri=None, declarations=None, imports=None, prefix=None):
        if prefix is not None:
            code = prefix + "\n\n" + code
        code = Annotator.injection.declarations(code, declarations)
        code = Annotator.injection.imports(code, imports)
        code = Annotator.injection.app(code)
        code = Annotator.injection.libs(code)
        code = Annotator.injection.namespace(code, app_id)
        code = Annotator.injection.cwd(code, app_id)
        code = Annotator.injection.baseuri(code, baseuri)
        code = Annotator.injection.dependencies(code)
        code = Annotator.injection.directives(code)
        return code
    
    def pug(self, code, app_id=None, baseuri=None):
        code = Annotator.injection.cwd(code, app_id=app_id)
        code = Annotator.injection.baseuri(code, baseuri=baseuri)
        return code

    def _search(self, target_file, result=[], extension=None):
        fs = self.fs()

        if fs.isdir(target_file):
            files = fs.files(target_file)
            for f in files:
                self._search(os.path.join(target_file, f), result=result, extension=extension)
            return result
        
        if extension is None:
            result.append(target_file)
            return result

        if os.path.splitext(target_file)[-1] == extension:
            result.append(os.path.join(*os.path.splitext(target_file)[:-1]))
            return result
        
        return result

    def _reconstruct(self):
        fs = self.fs()
        if fs.exists("config") == False:
            fs.makedirs("config")

        fs.write('build/wizbuild.js', Code.ESBUILD)
        fs.write('build/tsconfig.json', Code.TSCONFIG)
        if fs.exists('build/tailwind.config.js') == False:
            fs.write('build/tailwind.config.js', Code.TAILWIND)

        if fs.exists("src/angular/tailwind.config.js"):
            fs.write('build/tailwind.config.js', fs.read("src/angular/tailwind.config.js"))

        if fs.exists('build/src/environments') == False:
            fs.makedirs('build/src/environments')

        if fs.exists("src/angular/environment.ts"): fs.copy("src/angular/environment.ts", "build/src/environments/environment.ts")
        else: fs.write('build/src/environments/environment.ts', Code.ENV)
        fs.write('build/src/styles.scss', Code.STYLES)

        # clear build src files
        fs.delete("build/src/app")
        fs.delete("build/src/assets")
        fs.delete("build/src/controller")
        fs.delete("build/src/libs")
        fs.delete("build/src/model")
        fs.delete("build/src/route")
        fs.delete("build/src/styles")

        # copy src
        fs.copy("src/angular/main.ts", "build/src/main.ts")
        fs.copy("src/angular/wiz.ts", "build/src/wiz.ts")
        fs.copy("src/angular/index.pug", "build/src/index.pug")

        fs.copy("src/angular/app", "build/src/app")
        fs.copy("src/app", "build/src/app")
        fs.copy("src/assets", "build/src/assets")
        fs.copy("src/controller", "build/src/controller")
        fs.copy("src/model", "build/src/model")
        fs.copy("src/route", "build/src/route")
        fs.copy("src/angular/libs", "build/src/libs")
        fs.copy("src/angular/styles", "build/src/styles")

        # build portal
        def buildApp(module, mode="app"):
            apps = fs.ls(os.path.join("src/portal", module, mode))
            for app in apps:
                namespace = f"portal.{module}.{app}"
                srcpath = os.path.join("src/portal", module, mode, app)
                targetpath = os.path.join("build/src/app", namespace)
                fs.copy(srcpath, targetpath)
                appjson = fs.read.json(os.path.join(targetpath, "app.json"), dict())
                appjson['id'] = namespace
                appjson['mode'] = 'portal'
                appjson['path'] = os.path.join(srcpath, "app.json")
                if 'controller' in appjson and len(appjson['controller']) > 0:
                    appjson['controller'] = "portal/" + module + "/" + appjson['controller']
                fs.write.json(os.path.join(targetpath, "app.json"), appjson)

        def buildApi(module):
            apps = fs.ls(os.path.join("src/portal", module, "route"))
            for app in apps:
                namespace = f"portal.{module}.{app}"
                srcpath = fs.abspath(os.path.join("src/portal", module, "route", app))
                targetpath = os.path.join("build/src/route", namespace)
                fs.copy(srcpath, targetpath)
                appjson = fs.read.json(os.path.join(targetpath, "app.json"), dict())
                appjson['id'] = namespace
                if 'controller' in appjson and len(appjson['controller']) > 0:
                    appjson['controller'] = "portal/" + module + "/" + appjson['controller']
                fs.write.json(os.path.join(targetpath, "app.json"), appjson)

        def buildFiles(module, target, src):
            fs.makedirs(os.path.join("build", "src", src, "portal", module))
            files = fs.ls(os.path.join("src/portal", module, target))
            for f in files:
                fs.copy(fs.abspath(os.path.join("src/portal", module, target, f)), os.path.join("build", "src", src, "portal", module, f))

        modules = fs.ls("src/portal")
        for module in modules:
            info = fs.read.json(os.path.join("src/portal", module, "portal.json"), dict())
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
            if checker("libs"): buildFiles(module, "libs", "libs")
            if checker("styles"): buildFiles(module, "styles", "styles")

    def _build(self):
        fs = self.fs()
        baseuri = wiz.uri.ide()

        # build apps
        apps = []

        for app in fs.ls("build/src/app"):
            if fs.exists(os.path.join("build/src/app", app, "app.json")):
                app_id = app
                app = fs.read.json(os.path.join("build/src/app", app, "app.json"))
                viewts = fs.read(os.path.join("build/src/app", app_id, "view.ts"))

                # update app.json
                componentName = Namespace.componentName(app_id) + "Component"

                app['id'] = app_id
                app['path'] = f"./{app_id}/{app_id}.component"
                app['name'] = componentName

                componentInfo = Annotator.definition.ngComponentDesc(viewts)
                app["ng.build"] = dict(id=app_id, name=componentName, path="./" + app_id + "/" + app_id + ".component")
                ngtemplate = app["ng"] = dict(selector=Namespace.selector(app_id), **componentInfo)
                injector = [f'[{x}]=""' for x in ngtemplate['inputs']] + [f'({x})=""' for x in ngtemplate['outputs']]
                injector = ", ".join(injector)
                app['template'] = ngtemplate['selector'] + "(" + injector + ")"
                
                fs.write(os.path.join("build/src/app", app_id, "app.json"), json.dumps(app, indent=4))

                app['view.ts'] = viewts
                apps.append(app)

        # routing
        apps_routing = dict()
        for app in apps:
            try:
                if app['mode'] == 'page':
                    if app['layout'] not in apps_routing:
                        apps_routing[app['layout']] = []
                    if len(app['viewuri']) > 0:
                        routing_uri = app['viewuri']
                        if routing_uri[0] == "/":
                            routing_uri = routing_uri[1:]
                        apps_routing[app['layout']].append(dict(path=routing_uri, component=app['id'], app_id=app['id']))
            except Exception as e:
                pass

        app_routing_auto = [] 
        for layout in apps_routing:
            children = []
            for child in apps_routing[layout]:
                children.append(child)
            app_routing_auto.append(dict(component=layout, children=children))
        
        app_routing_auto = json.dumps(app_routing_auto, indent=4)
        app_routing_auto = Annotator.injection.route(app_routing_auto)
        
        # prefix and imports
        prefix = [dict(name=x['name'], path=x['path']) for x in apps]        
        imports = []
        declarations = [x['name'] for x in apps]

        for app in apps:
            app_id = app['id']
            code = app['view.ts']
            deps = Annotator.definition.dependencies(code)

            for dep in deps:
                pkg = deps[dep]
                tmp = dict(name=dep, path=pkg)
                if tmp not in prefix:
                    prefix.append(tmp)
                if dep not in imports:
                    imports.append(dep)
            
            deps = Annotator.definition.directives(code)
            for dep in deps:
                pkg = deps[dep]
                tmp = dict(name=dep, path=pkg)
                if tmp not in prefix:
                    prefix.append(tmp)
                if dep not in declarations:
                    declarations.append(dep)
        
        prefix = "\n".join(["import { " + x['name'] + " } from '" + x['path'] + "';" for x in prefix])
        imports = ",\n".join(["        " + x for x in imports])
        declarations = "AppComponent,\n" + ",\n".join(["        " + x for x in declarations])

        # build pug
        targets = self._search("build/src", result=[], extension=".pug")
        for target in targets:
            code = fs.read(target + ".pug")
            filename = target.split("/")[-1]
            if filename == 'view':
                app_id = target.split("/")[-2]
                code = self.pug(code, baseuri=baseuri, app_id=app_id)
            else:
                code = self.pug(code, baseuri=baseuri)
            fs.write(target + ".pug", code)
        
        # build typescript
        targets = self._search("build/src/app", result=[], extension=".ts")
        for target in targets:
            code = fs.read(target + ".ts")
            filename = target.split("/")[-1]
            
            if filename == 'view':
                app_id = target.split("/")[-2]

                # if view.ts
                importString = "import { Component } from '@angular/core';\n"
                componentName = Namespace.componentName(app_id)
                componentOpts = "{\n    selector: '" + Namespace.selector(app_id) + "',\n    templateUrl: './view.html',\n    styleUrls: ['./view.scss']\n}"

                code = f"import Wiz from 'src/wiz';\nlet wiz = new Wiz('{baseuri}').app('{app_id}');\n" + code
                code = code.replace('export class Component', f"@Component({componentOpts})\n" + f'export class {componentName}Component')
                code = f"{importString}\n" + code.strip()
                code = code + f"\n\nexport default {componentName}Component;"

                fs.delete(target + ".ts")
                target = os.path.join(os.path.dirname(target), app_id + ".component")

                code = self.typescript(code, baseuri=baseuri, app_id=app_id, declarations=declarations, imports=imports)
            elif filename == 'app-routing.module':
                code = code.replace("wiz.routes()", app_routing_auto)
                code = self.typescript(code, baseuri=baseuri, declarations=declarations, imports=imports, prefix=prefix)
            elif filename == 'app.component':
                code = f"import Wiz from 'src/wiz';\nlet wiz = new Wiz('{baseuri}');\n" + code
                code = self.typescript(code, baseuri=baseuri)
            elif filename == 'app.module':
                code = self.typescript(code, baseuri=baseuri, declarations=declarations, imports=imports, prefix=prefix)
            else:
                code = self.typescript(code, baseuri=baseuri)
            fs.write(target + ".ts", code)

        # build pug files
        targets = self._search("build/src", result=[], extension=".pug")
        if len(targets) > 0:
            targets = " ".join(targets)
            build_base_path = fs.abspath()
            Util.execute(f"cd {build_base_path} && node build/wizbuild {targets}")
        
        # build angular json
        angularJson = fs.read.json("src/angular/angular.json", dict())
        angularBuildOptionsJson = "src/angular/angular.build.options.json"
        if fs.exists(angularBuildOptionsJson):
            angularBuildOptionsJson = fs.read.json(angularBuildOptionsJson, dict())
            for key in angularBuildOptionsJson:
                if key in ["outputPath", "index", "main", "polyfills", "tsConfig", "inlineStyleLanguage"]: continue
                angularJson["projects"]["build"]["architect"]["build"]["options"][key] = angularBuildOptionsJson[key]
        fs.write("build/angular.json", json.dumps(angularJson, indent=4))
        fs.write("src/angular/angular.json", json.dumps(angularJson, indent=4))

        # build tailwindcss
        if fs.exists("./build/node_modules/.bin/tailwindcss"):
            build_base_path = fs.abspath("build")
            Util.execute(f"cd {build_base_path} && node_modules/.bin/tailwindcss -o tailwind.min.css --minify", False)

    def _angular(self):
        fs = self.fs()
        esbuildpath = fs.abspath('build')
        Util.execute(f"cd {esbuildpath} && node wizbuild")

Model = Model()