import os
import season
import json
import re
from season.core.builder.base import Build as BaseBuild
from season.core.builder.base import Compiler as BaseCompiler
from season.core.builder.base import Converter as BaseConverter
from season.core.builder.base import ESBUILD_SCRIPT, ENV_SCRIPT

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

class Converter(BaseConverter):

    def syntax(self, code, **skwargs):
        kwargs = self.kwargs.copy()
        for key in skwargs:
            kwargs[key] = skwargs[key]

        code = self.wrapper(self.syntax_title, code, **kwargs)
        code = self.wrapper(self.syntax_app, code, **kwargs)
        code = self.wrapper(self.syntax_service, code, **kwargs)
        code = self.wrapper(self.syntax_libs, code, **kwargs)
        code = self.wrapper(self.syntax_namespace, code, **kwargs)
        code = self.wrapper(self.syntax_cwd, code, **kwargs)
        code = self.wrapper(self.syntax_baseuri, code, **kwargs)
        code = self.wrapper(self.syntax_module_declarations, code, **kwargs)
        code = self.wrapper(self.syntax_module_imports, code, **kwargs)
        code = self.wrapper(self.syntax_dependencies, code, **kwargs)
        code = self.wrapper(self.syntax_directives, code, **kwargs)

        return code
    
    def syntax_title(self, code, title):
        pattern = r'@wiz.title\((.*)\)'
        def convert(match_obj):
            return title
        code = re.sub(pattern, convert, code)
        code = code.replace("@wiz.title", title)
        return code

class Compiler(BaseCompiler):
    def __init__(self, build, srcfs, buildfs, distfs):
        self.params = self.build_params(build, srcfs, buildfs, distfs)
        baseuri = self.params.baseuri = self.params.wiz.uri.ide()
        title = self.params.wiz.server.config.service.title
        self.params.converter = Converter(baseuri=baseuri, title=title)

class Build(BaseBuild):
    def __init__(self, workspace):
        super().__init__(workspace)

    def params(self):
        obj = super().params()
        obj.fs.build = obj.workspace.fs("build")
        obj.fs.src = obj.workspace.fs()
        obj.fs.dist = obj.workspace.fs(os.path.join("build", "dist", "build"))

        obj.buildfs = obj.fs.build
        obj.distfs = obj.fs.dist
        obj.srcfs = obj.fs.src

        obj.path = obj.buildfs.abspath()
        return obj

    # init project build
    def event_init(self, workspace, config, srcfs, buildfs, workspacefs, execute):
        working_dir = workspacefs.abspath()
        build_dir = buildfs.abspath()
        build_name = 'build'
        if buildfs.exists():
            return

        command_ng = f"{working_dir}/node_modules/@angular/cli/bin/ng.js"
        execute(f'cd {working_dir} && npm i @angular/cli')
        execute(f'cd {working_dir} && {command_ng} new {build_name} --routing true --style scss --interactive false  --skip-tests true --skip-git true')
        
        buildfs.write('wizbuild.js', ESBUILD_SCRIPT)
        buildfs.write(os.path.join('src', 'environments', 'environment.ts'), ENV_SCRIPT)

        if srcfs.isfile(os.path.join("angular", "package.json")):
            buildfs.copy(srcfs.abspath(os.path.join("angular", "package.json")), "package.json")
            execute(f"cd {build_dir} && npm install")
        else:
            execute(f"cd {build_dir} && npm install ngc-esbuild pug jquery socket.io-client --save")

    # build on src updated
    def event_build(self, wiz, workspace, filepath, srcfs, distfs, buildfs, config, execute):
        if len(filepath) == 0:
            buildfs.delete("src/app")
            buildfs.delete("src/service")
            buildfs.delete("src/libs")
        
            wpfs = workspace.fs()
            wpfs.delete("app")
            wpfs.makedirs("app")

            pluginfs = workspace.fs("..", "plugin")
            plugins = pluginfs.ls()

            shortcutcode = "import Service from './service';\n"
            shortcutcode += "import { KeyMod, KeyCode } from 'monaco-editor';\n\n"

            for plugin in plugins:
                pluginpath = os.path.join(plugin, "plugin.json")
                if pluginfs.exists(pluginpath) == False:
                    continue
                plugininfo = pluginfs.read.json(pluginpath)
                if plugininfo is None:
                    continue

                shortcutpath = os.path.join(plugin, "shortcut.ts")
                if pluginfs.exists(shortcutpath):
                    code = pluginfs.read(shortcutpath)
                    shortcutcode += shortcutCodeBuilder(f"class {plugin}", code) + "\n"
                
                apptypes = ['app', 'editor', 'system']
                for apptype in apptypes:
                    appsrcpath = os.path.join(plugin, apptype)
                    if pluginfs.exists(appsrcpath) == False: continue
                    apps = pluginfs.ls(appsrcpath)

                    for app in apps:
                        apppath = os.path.join(plugin, apptype, app)
                        app_id = f"{plugin}.{apptype}.{app}"
                        wpfs.copy(pluginfs.abspath(apppath), os.path.join("app", app_id))

            wpfs.write(os.path.join("angular/service/shortcut.plugin.ts"), shortcutcode)

            configfs = workspace.fs("..", "config")

            shortcutcode = "import Service from './service';\n"
            shortcutcode += "import { KeyMod, KeyCode } from 'monaco-editor';\n\n"
            code = configfs.read("shortcut.ts", "[]")
            shortcutcode += shortcutCodeBuilder("default class shortcut", code) + "\n"
            wpfs.write(os.path.join("angular/service/shortcut.custom.ts"), shortcutcode)

            menus = configfs.read.json("plugin.json", dict())

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
            wpfs.write(os.path.join("app", "core.system.config.leftmenu", "view.pug"), pug)

            pug = []
            if 'overlay' in menus:
                pug = build_menu_pug(menus['overlay'], pug)
            pug = "\n".join(pug)
            wpfs.write(os.path.join("app", "core.system.overlay", "view.pug"), pug)
            
            pug = []
            if 'app' in menus:
                pug = build_menu_pug(menus['app'], pug)
            if 'setting' in menus:
                pug = build_menu_pug(menus['setting'], pug)
            pug = "\n".join(pug)
            wpfs.write(os.path.join("app", "core.system.config.rightmenu", "view.pug"), pug)
            configfs.copy("plugin.json", wpfs.abspath(os.path.join("angular", "libs", "plugin.json")))

        baseuri = wiz.uri.ide()
        title = wiz.server.config.service.title
        build_folder = 'build'
        compiler = Compiler(self, srcfs, buildfs, distfs)
        converter = Converter(baseuri=baseuri, title=title)
        
        pugfiles = []

        # build single files
        def build_file(target_file):
            segment = target_file.split("/")

            # if not allowed target
            if segment[0] not in ['angular', 'app', '']:
                return
            
            # if target is directory
            if srcfs.isdir(target_file):
                files = srcfs.files(target_file)
                for file in files:
                    build_file(os.path.join(target_file, file))
                return

            # compile
            action, target = compiler(target_file)
            if action == 'pug':
                pugfiles.append(target)

        build_file(filepath)

        # compile pug files as bulk
        pugfilepaths = " ".join(pugfiles)
        if len(pugfiles) > 0:
            execute(f"cd {buildfs.abspath()} && node wizbuild {pugfilepaths}")

        for pugfile in pugfiles:
            pugfile = pugfile[len(srcfs.abspath()) + 1:]
            target = pugfile.split("/")[0]
            htmlfile = pugfile + ".html"
            
            copyfile = None

            if target == 'app':
                copyfile = os.path.join("src", pugfile + ".html")
                copyfolder = os.path.dirname(copyfile)
                if buildfs.isdir(copyfolder) == False:
                    buildfs.makedirs(copyfolder)
                buildfs.copy(srcfs.abspath(htmlfile), copyfile)
            elif htmlfile == 'angular/index.html':
                copyfile = os.path.join("src", "index.html")
                text = srcfs.read(htmlfile)
                text = converter.syntax(text)
                buildfs.write(copyfile, text)
            elif htmlfile == 'angular/app/app.component.html':
                copyfile = os.path.join("src", "app", "app.component.html")
                text = srcfs.read(htmlfile)
                text = converter.syntax(text)
                buildfs.write(copyfile, text)
            else:
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
        
        # auto build: app.module.ts
        component_declarations = "AppComponent,\n" + ",\n".join(["        " + x['name'] for x in apps])
        component_import = "\n".join(["import { " + x['name'] + " } from '" + x['path'] + "';" for x in apps])
        ngmodule_imports = []

        apps = srcfs.files(os.path.join("app"))
        for app in apps:
            if srcfs.exists(os.path.join("app", app, "view.ts")):
                text = srcfs.read(os.path.join("app", app, "view.ts"))
                text = converter.syntax_cwd(text, app_id=app)
                text = converter.syntax_namespace(text, app_id=app)
                
                deps = converter.dependencies(text)
                for dep in deps:
                    pkg = deps[dep]
                    if dep not in ngmodule_imports:
                        component_import = component_import + "\nimport { "+ dep +" } from '" + pkg + "'"
                        ngmodule_imports.append(dep)

                deps = converter.directives(text)
                for dep in deps:
                    pkg = deps[dep]
                    if dep not in ngmodule_imports:
                        component_import = component_import + "\nimport { "+ dep +" } from '" + pkg + "'"
                    component_declarations = component_declarations + ",\n        " + dep

        ngmodule_imports = ",\n".join(["        " + x for x in ngmodule_imports])

        app_module_ts = srcfs.read(os.path.join("angular", "app", "app.module.ts"))
        app_module_ts = component_import + "\n\n" + app_module_ts
        app_module_ts = converter.syntax(app_module_ts, declarations=component_declarations, imports=ngmodule_imports)
        buildfs.write(os.path.join("src", "app", "app.module.ts"), app_module_ts)

        # run esbuild
        execute(f"cd {buildfs.abspath()} && node wizbuild")
        srcfs.copy(buildfs.abspath("package.json"), os.path.join("angular", "package.json"))
