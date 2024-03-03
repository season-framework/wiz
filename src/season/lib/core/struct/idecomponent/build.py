import os
import sys
import subprocess
import json
from .util.namespace import Namespace
from .util.annotator import Annotator

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

TSCONFIG_SCRIPT = """{
  "compileOnSave": false,
  "compilerOptions": {
    "baseUrl": "./",
    "outDir": "./dist/out-tsc",
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "sourceMap": true,
    "declaration": false,
    "downlevelIteration": true,
    "experimentalDecorators": true,
    "moduleResolution": "node",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "useDefineForClassFields": false,
    "lib": [
      "ES2022",
      "dom"
    ]
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}
"""

LOG_DEBUG = 0
LOG_INFO = 1
LOG_WARN = LOG_WARNING = 2
LOG_DEV = 3
LOG_ERR = LOG_ERROR = 4
LOG_CRIT = LOG_CRITICAL = 5

class Build:
    def __init__(self, wiz):
        self.wiz = wiz
        self.python_executable = str(sys.executable)
        self.annotator = Annotator
        self.namespace = Namespace

    def __call__(self):
        self.install()
        self._reconstruct()
        self._build()
        self._angular()
        self.wiz.server.cache.clear()

    def execute(self, cmd):
        wiz = self.wiz
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        
        if out is not None and len(out) > 0: 
            out = out.decode('utf-8').strip()
            wiz.logger('ide/build/log')(out)
        if err is not None and len(err) > 0: 
            err = err.decode('utf-8').strip()
            if "npm WARN" in err or "- Installing packages (npm)" in err:
                wiz.logger('ide/build/log')(err, level=LOG_WARNING)
            else: 
                wiz.logger('ide/build/error')(err, level=LOG_CRITICAL)

    def searchFiles(self, target_file, result=[], extension=None):
        fs = self.wiz.fs("ide")

        if fs.isdir(target_file):
            files = fs.files(target_file)
            for f in files:
                self.searchFiles(os.path.join(target_file, f), result=result, extension=extension)
            return result
        
        if extension is None:
            result.append(target_file)
            return result

        if os.path.splitext(target_file)[-1] == extension:
            result.append(os.path.join(*os.path.splitext(target_file)[:-1]))
            return result
        
        return result

    def typescript(self, code, app_id=None, baseuri=None, declarations=None, imports=None, title=None, prefix=None):
        code = Annotator.injection.declarations(code, declarations)
        code = Annotator.injection.imports(code, imports)

        code = Annotator.injection.title(code, title)
        code = Annotator.injection.app(code)
        code = Annotator.injection.service(code)
        code = Annotator.injection.libs(code)
        code = Annotator.injection.namespace(code, app_id)
        code = Annotator.injection.cwd(code, app_id)
        code = Annotator.injection.baseuri(code, baseuri)
        code = Annotator.injection.dependencies(code)
        code = Annotator.injection.directives(code)

        if prefix is not None:
            code = prefix + "\n\n" + code

        return code
    
    def pug(self, code, app_id=None, baseuri=None, title=None):
        code = Annotator.injection.title(code, title)
        code = Annotator.injection.cwd(code, app_id=app_id)
        code = Annotator.injection.baseuri(code, baseuri=baseuri)
        return code

    def clean(self):
        fs = self.wiz.fs("ide")
        fs.delete("app")
        fs.delete("build")
        fs.delete("node_modules")
        fs.delete("package-lock.json")

    def install(self):
        fs = self.wiz.fs("ide")
        if fs.exists("build"):
            return
        
        working_dir = fs.abspath()
        build_dir = fs.abspath("build")
        self.execute(f'cd {working_dir} && npm i')

        command_ng = f"{working_dir}/node_modules/@angular/cli/bin/ng.js"
        self.execute(f'cd {working_dir} && {command_ng} new build --routing true --style scss --interactive false  --skip-tests true --skip-git true')

        if fs.isfile("angular/package.json"):
            packageJson = fs.read.json("angular/package.json")
            fs.write.json("build/package.json", packageJson)
            self.execute(f"cd {build_dir} && npm install --force")
        else:
            self.execute(f"cd {build_dir} && npm install ngc-esbuild pug jquery socket.io-client --save")

    def _reconstruct(self):
        fs = self.wiz.fs()

        fs.write('ide/build/wizbuild.js', ESBUILD_SCRIPT)
        fs.write('ide/build/tsconfig.json', TSCONFIG_SCRIPT)
        fs.write('ide/build/src/environments/environment.ts', ENV_SCRIPT)

        # initialize directory
        fs.delete(os.path.join("ide", "app"))
        fs.makedirs(os.path.join("ide", "app"))

        # shortcut preset
        def shortcutCodeBuilder(name, shortcutcode):
            PS = "{"
            PE = "}"

            return f"""export {name} {PS}
            constructor(private service: Service) {PS} {PE}

            public bind() {PS}
                let service = this.service;
                let shortcuts = {shortcutcode};

                for (let i = 0 ; i < shortcuts.length ; i++) {PS}
                    let name = shortcuts[i].name;
                    if(!name) continue;
                    this.service.shortcut.bind(name, shortcuts[i]);
                {PE}
            {PE}
        {PE}
        """

        shortcutcode = "import Service from './service';\n"
        shortcutcode += "import { KeyMod, KeyCode } from 'monaco-editor';\n\n"

        # install plugin
        plugins = fs.ls("plugin")
        for plugin in plugins:
            pluginpath = os.path.join("plugin", plugin, "plugin.json")
            if fs.exists(pluginpath) == False:
                continue
            plugininfo = fs.read.json(pluginpath)
            if plugininfo is None:
                continue

            shortcutpath = os.path.join("plugin", plugin, "shortcut.ts")
            if fs.exists(shortcutpath):
                code = fs.read(shortcutpath)
                shortcutcode += shortcutCodeBuilder(f"class {plugin}", code) + "\n"

            apptypes = ['app', 'editor', 'system']
            for apptype in apptypes:
                appsrcpath = os.path.join("plugin", plugin, apptype)
                if fs.exists(appsrcpath) == False: continue
                apps = fs.ls(appsrcpath)

                for app in apps:
                    apppath = os.path.join("plugin", plugin, apptype, app)
                    app_id = f"{plugin}.{apptype}.{app}"
                    fs.copy(fs.abspath(apppath), os.path.join("ide", "app", app_id))
        
        # write shortcut config
        fs.write(os.path.join("ide", "angular", "service", "shortcut.plugin.ts"), shortcutcode)

        shortcutcode = "import Service from './service';\n"
        shortcutcode += "import { KeyMod, KeyCode } from 'monaco-editor';\n\n"
        code = fs.read(os.path.join("config", "shortcut.ts"), "[]")
        shortcutcode += shortcutCodeBuilder("default class shortcut", code) + "\n"
        fs.write(os.path.join("ide", "angular", "service", "shortcut.custom.ts"), shortcutcode)

        # build menu
        menus = fs.read.json(os.path.join("config", "plugin.json"), dict())
        
        def build_menu_pug(targets, pug):
            for menu in targets:
                namespace = menu["id"]
                attributes = ['*ngIf="menu.mode == ' + "'" + menu["id"] + "'" + '"']
                if "values" in menu:
                    values = menu["values"]
                    for key in values:
                        v = values[key]
                        attributes.append(f'[{key}]="{v}"')
                if "event" in menu:
                    values = menu["event"]
                    for key in values:
                        v = values[key]
                        attributes.append(f'({key})="{v}"')
                
                template = "wiz-" + namespace.replace(".", "-") + '(' + ", ".join(attributes) + ')'
                pug.append(template)
            return pug
    
        pug = []
        if 'main' in menus:
            pug = build_menu_pug(menus['main'], pug)
        if 'sub' in menus:
            pug = build_menu_pug(menus['sub'], pug)
        pug = "\n".join(pug)
        fs.write(os.path.join("ide", "app", "core.system.config.leftmenu", "view.pug"), pug)

        pug = []
        if 'overlay' in menus:
            pug = build_menu_pug(menus['overlay'], pug)
        pug = "\n".join(pug)
        fs.write(os.path.join("ide", "app", "core.system.overlay", "view.pug"), pug)

        pug = []
        if 'app' in menus:
            pug = build_menu_pug(menus['app'], pug)
        if 'setting' in menus:
            pug = build_menu_pug(menus['setting'], pug)
        pug = "\n".join(pug)
        fs.write(os.path.join("ide", "app", "core.system.config.rightmenu", "view.pug"), pug)

        fs.copy(os.path.join("config", "plugin.json"), fs.abspath(os.path.join("ide", "angular", "libs", "plugin.json")))

        fs.delete(os.path.join("ide", "build", "src", "app"))
        fs.delete(os.path.join("ide", "build", "src", "assets"))
        fs.delete(os.path.join("ide", "build", "src", "libs"))
        fs.delete(os.path.join("ide", "build", "src", "service"))
        fs.delete(os.path.join("ide", "build", "src", "styles"))

        fs.copy(os.path.join("ide", "angular", "main.ts"), os.path.join("ide", "build", "src", "main.ts"))
        fs.copy(os.path.join("ide", "angular", "wiz.ts"), os.path.join("ide", "build", "src", "wiz.ts"))
        fs.copy(os.path.join("ide", "angular", "index.pug"), os.path.join("ide", "build", "src", "index.pug"))

        fs.copy(os.path.join("ide", "angular", "app"), os.path.join("ide", "build", "src", "app"))
        fs.copy(os.path.join("ide", "assets"), os.path.join("ide", "build", "src", "assets"))
        fs.copy(os.path.join("ide", "angular", "libs"), os.path.join("ide", "build", "src", "libs"))
        fs.copy(os.path.join("ide", "angular", "service"), os.path.join("ide", "build", "src", "service"))
        fs.copy(os.path.join("ide", "angular", "styles"), os.path.join("ide", "build", "src"))
        fs.copy(os.path.join("ide", "app"), os.path.join("ide", "build", "src", "app"))
        
    def _build(self):
        fs = self.wiz.fs("ide")
        baseuri = self.wiz.uri.ide("ide")
        title = self.wiz.server.config.ide.title

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
        targets = self.searchFiles("build/src", result=[], extension=".pug")
        for target in targets:
            code = fs.read(target + ".pug")
            filename = target.split("/")[-1]
            if filename == 'view':
                app_id = target.split("/")[-2]
                code = self.pug(code, baseuri=baseuri, title=title, app_id=app_id)
            else:
                code = self.pug(code, baseuri=baseuri, title=title)

            fs.write(target + ".pug", code)

        # build typescript
        targets = self.searchFiles("build/src/app", result=[], extension=".ts")
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

                code = self.typescript(code, baseuri=baseuri, app_id=app_id, declarations=declarations, imports=imports, title=title)
        
            elif filename == 'service':
                code = self.typescript(code, baseuri=baseuri, declarations=declarations, imports=imports, title=title)

            elif filename == 'app.component':
                code = f"import Wiz from 'src/wiz';\nlet wiz = new Wiz('{baseuri}');\n" + code
                code = self.typescript(code, baseuri=baseuri, title=title)

            elif filename == 'app.module':
                code = self.typescript(code, baseuri=baseuri, declarations=declarations, imports=imports, prefix=prefix, title=title)
            
            else:
                code = self.typescript(code, baseuri=baseuri, title=title)

            fs.write(target + ".ts", code)

        # build pug files
        targets = self.searchFiles("build/src", result=[], extension=".pug")
        if len(targets) > 0:
            targets = " ".join(targets)
            build_base_path = fs.abspath()
            self.execute(f"cd {build_base_path} && node build/wizbuild {targets}")

        # angularjson
        angularjson = fs.read.json("build/angular.json", dict())
        angularBuildOptionsJson = "angular/angular.build.options.json"
        if fs.exists(angularBuildOptionsJson):
            angularBuildOptionsJson = fs.read.json(angularBuildOptionsJson, dict())
            for key in angularBuildOptionsJson:
                if key in ["outputPath", "index", "main", "polyfills", "tsConfig", "inlineStyleLanguage"]: continue
                angularjson["projects"]["build"]["architect"]["build"]["options"][key] = angularBuildOptionsJson[key]
        fs.write("build/angular.json", json.dumps(angularjson, indent=4))

    def _angular(self):
        fs = self.wiz.fs("ide")
        esbuildpath = fs.abspath('build')
        self.execute(f"cd {esbuildpath} && node wizbuild")