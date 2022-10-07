import os
import season
import json
import re
from season.core.builder.base import Build as BaseBuild
from season.core.builder.base import Compiler as BaseCompiler
from season.core.builder.base import Converter as BaseConverter
from season.core.builder.base import ESBUILD_SCRIPT, ENV_SCRIPT

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
        command_ng = config.command_ng

        if buildfs.exists():
            return

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
