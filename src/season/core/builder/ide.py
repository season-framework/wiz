import os
import season
import json
import re
from season.core.builder.base import Build as Base, ESBUILD_SCRIPT, ENV_SCRIPT

class Converter:
    def __init__(self, **kwargs):
        self.kwargs = dict(app_id=None, declarations=None, baseuri=None, title=None, imports=None)
        for key in kwargs:
            self.kwargs[key] = kwargs[key]

    def component_name(self, namespace):
        app_id_split = namespace.split(".")
        componentname = []
        for wsappname in app_id_split:
            componentname.append(wsappname.capitalize())
        componentname = "".join(componentname)
        return componentname
    
    def component_selector(self, namespace):
        return "wiz-" + "-".join(namespace.split("."))

    def dependencies(self, code):
        result = dict()
        pattern = re.compile('@dependencies\(([^\).]*)\)', re.DOTALL)
        res = pattern.findall(code)
        for data in res:
            data = data.replace("'", '').replace('"', '').replace(',', '').replace(' ', '')
            pattern = re.compile('(.*):(.*)')
            finded = pattern.findall(data)
            for item in finded:
                result[item[0]] = item[1]
        return result

    def syntax_route(self, code):
        def convert(match_obj):
            val = match_obj.group(1)
            return 'component: ' + self.component_name(val) + "Component"
        pattern = r"component.*:.*'(.*)'"
        code = re.sub(pattern, convert, code)
        pattern = r'component.*:.*"(.*)"'
        code = re.sub(pattern, convert, code)
        return code
    
    def syntax(self, code, **skwargs):
        kwargs = self.kwargs.copy()
        for key in skwargs:
            kwargs[key] = skwargs[key]

        fncall = season.util.fn.call
        def wrapper(fn, code):
            try: 
                kwargs['code'] = code
                return fncall(fn, **kwargs)
            except:
                return code
        code = wrapper(self.syntax_title, code)        
        code = wrapper(self.syntax_app, code)
        code = wrapper(self.syntax_service, code)
        code = wrapper(self.syntax_namespace, code)
        code = wrapper(self.syntax_baseuri, code)
        code = wrapper(self.syntax_module_declarations, code)
        code = wrapper(self.syntax_module_imports, code)
        code = wrapper(self.syntax_dependencies, code)
        return code

    def syntax_dependencies(self, code):
        def convert(match_obj):
            val1 = match_obj.group(1)
            return ""
        pattern = re.compile('@dependencies\(([^\).]*)\)', re.DOTALL)
        code = re.sub(pattern, convert, code)
        return code

    def syntax_app(self, code):
        def convert(match_obj):
            val = match_obj.group(1)
            if len(val.split("/")) > 1:
                return f'"src/app/{val}"'
            return f'"src/app/{val}/{val}.component"'
        pattern = r'"@wiz\/app\/(.*)"'
        code = re.sub(pattern, convert, code)
        pattern = r"'@wiz\/app\/(.*)'"
        code = re.sub(pattern, convert, code)
        return code

    def syntax_service(self, code):
        def convert(match_obj):
            val = match_obj.group(1)
            return f'"src/service/{val}"'
        pattern = r'"@wiz\/service\/(.*)"'
        code = re.sub(pattern, convert, code)
        pattern = r"'@wiz\/service\/(.*)'"
        code = re.sub(pattern, convert, code)
        return code

    def syntax_title(self, code, title):
        pattern = r'@wiz.title\((.*)\)'
        def convert(match_obj):
            return title
        code = re.sub(pattern, convert, code)
        code = code.replace("@wiz.title", title)
        return code

    def syntax_namespace(self, code, app_id):
        if app_id is None: return code
        pattern = r'@wiz.namespace\((.*)\)'
        def convert(match_obj):
            return app_id
        code = re.sub(pattern, convert, code)
        code = code.replace("@wiz.namespace", app_id)
        return code

    def syntax_baseuri(self, code, baseuri):
        if baseuri is None: return code
        pattern = r'@wiz.baseuri\((.*)\)'
        def convert(match_obj):
            val = match_obj.group(1)
            if len(val) > 0:
                if val[0] == "/":
                    val = val[1:]
                return baseuri + "/" + val
            return baseuri
        code = re.sub(pattern, convert, code)
        code = code.replace("@wiz.baseuri", baseuri)
        return code
    
    def syntax_module_declarations(self, code, declarations):
        if declarations is None: return code
        pattern = r'"@wiz.declarations\((.*)\)"'
        def convert(match_obj):
            return declarations
        code = re.sub(pattern, convert, code)
        pattern = r"'@wiz.declarations\((.*)\)'"
        def convert(match_obj):
            return declarations
        code = re.sub(pattern, convert, code)
        code = code.replace("'@wiz.declarations'", declarations)
        code = code.replace('"@wiz.declarations"', declarations)
        return code

    def syntax_module_imports(self, code, imports):
        if imports is None: return code
        pattern = r'"@wiz.imports\((.*)\)"'
        def convert(match_obj):
            return imports
        code = re.sub(pattern, convert, code)
        pattern = r"'@wiz.imports\((.*)\)'"
        def convert(match_obj):
            return imports
        code = re.sub(pattern, convert, code)
        code = code.replace("'@wiz.imports'", imports)
        code = code.replace('"@wiz.imports"', imports)
        return code

class Compiler:
    def __init__(self, build, srcfs, buildfs, distfs):
        self.params = season.util.std.stdClass()
        self.params.build = build
        self.params.workspace = build.workspace
        self.params.wiz = build.workspace.wiz
        self.params.srcfs = srcfs
        self.params.buildfs = buildfs
        self.params.distfs = distfs
        
        baseuri = self.params.wiz.uri.ide()
        title = self.params.wiz.server.config.service.title
        self.params.converter = Converter(baseuri=baseuri, title=title)

    def __call__(self, filepath):
        self.params.filepath = filepath
        self.params.basename = os.path.basename(filepath)
        self.params.extension = os.path.splitext(filepath)[-1]
        self.params.segment = filepath.split("/")
        self.params.mode = self.params.segment[0]
        return season.util.fn.call(self.__caller__, **self.params)

    def __caller__(self, srcfs, buildfs, distfs, filepath, basename, extension, segment, mode):
        if extension == '.pug':
            return 'pug', srcfs.abspath(filepath[:-len(extension)])

        if mode == 'app':
            buildfile = os.path.join("src", filepath)
            buildfolder = os.path.dirname(buildfile)
            if buildfs.isdir(buildfolder) == False:
                buildfs.makedirs(buildfolder)

            if basename == 'service.ts':
                return season.util.fn.call(self.app_service_ts, buildfile=buildfile, **self.params)

            if basename == 'view.ts':
                return season.util.fn.call(self.app_view_ts, buildfile=buildfile, **self.params)
            
            return season.util.fn.call(self.app_files, buildfile=buildfile, **self.params)
        
        if mode == 'angular':
            ngtarget = segment[1]

            if ngtarget == 'styles':
                buildfile = os.path.join("src", *segment[2:])
                return season.util.fn.call(self.ng_styles, buildfile=buildfile, **self.params)

            ngfilepath = os.path.join(*segment[1:])
            buildfile = os.path.join("src", *segment[1:])
            buildfolder = os.path.dirname(buildfile)
            if buildfs.isdir(buildfolder) == False:
                buildfs.makedirs(buildfolder)

            if ngtarget == 'service':
                return season.util.fn.call(self.ng_service, buildfile=buildfile, **self.params)

            if ngtarget == 'angular.build.options.json':
                return season.util.fn.call(self.ng_angular_json, buildfile=buildfile, **self.params)

            if ngtarget == 'app' and ngfilepath == 'app/app.component.ts':
                return season.util.fn.call(self.ng_app_component, buildfile=buildfile, **self.params)

            if ngtarget in ['app', 'wiz.ts']:
                return season.util.fn.call(self.ng_files, buildfile=buildfile, **self.params)

        return None, None

    def app_files(self, filepath, buildfile, srcfs, buildfs):
        buildfs.copy(srcfs.abspath(filepath), buildfile)
        return 'app/files', True

    def app_service_ts(self, wiz, filepath, buildfs, srcfs, segment, converter):
        app_id = segment[1]
        baseuri = wiz.uri.ide()
        
        code = srcfs.read(filepath)
        code = f"import Wiz from 'src/wiz';\nlet wiz = new Wiz('{baseuri}').app('{app_id}');\n" + code
        code = code.replace("export class", "import { Injectable } from '@angular/core';\n\n@Injectable({ providedIn: 'root' })\nexport class")
        buildfile = os.path.join('src', os.path.dirname(filepath), "service.ts")
        buildfs.write(buildfile, code)
        return 'app/service_ts', True

    def app_view_ts(self, wiz, filepath, buildfs, srcfs, segment, converter):
        appjsonfile = os.path.join(os.path.dirname(filepath), "app.json")
        app_id = segment[1]
        componentname = converter.component_name(app_id)
        appjson = srcfs.read.json(appjsonfile, dict())

        importstr = "import { Component } from '@angular/core';\n"
     
        baseuri = wiz.uri.ide()
        
        # read src code
        code = srcfs.read(filepath)
        code = f"import Wiz from 'src/wiz';\nlet wiz = new Wiz('{baseuri}').app('{app_id}');\n" + code

        # convert syntax
        code = converter.syntax(code, app_id=app_id)

        # convert export class
        code = code.replace('export class Component', "@Component({\n    selector: '" + converter.component_selector(app_id) + "',\n    templateUrl: './view.html',\n    styleUrls: ['./view.scss']\n})\n" + f'export class {componentname}Component')
        code = f"{importstr}\n" + code.strip()
        code = code + f"\n\nexport default {componentname}Component;"

        buildfile = os.path.join('src', os.path.dirname(filepath), app_id + ".component.ts")
        buildfs.write(buildfile, code)

        appjson["ng.build"] = dict(id=app_id, name=componentname + "Component", path="./" + app_id + "/" + app_id + ".component")
        srcfs.write(appjsonfile, json.dumps(appjson, indent=4))

        return 'app/view_ts', True

    def ng_files(self, filepath, buildfile, srcfs, buildfs):
        buildfs.copy(srcfs.abspath(filepath), buildfile)
        return 'angular/files', True

    def ng_app_component(self, wiz, filepath, buildfile, buildfs, srcfs, converter):
        baseuri = wiz.uri.ide()
        code = srcfs.read(filepath)
        code = f"import Wiz from 'src/wiz';\nlet wiz = new Wiz('{baseuri}');\n" + code
        code = converter.syntax(code)
        buildfs.write(buildfile, code)
        return 'app/app.component.ts', True

    def ng_service(self, filepath, buildfile, srcfs, buildfs):
        code = srcfs.read(filepath)
        code = code.replace("export class", "import { Injectable } from '@angular/core';\n\n@Injectable({ providedIn: 'root' })\nexport class")
        buildfs.write(buildfile, code)
        return 'angular/service', True

    def ng_styles(self, filepath, buildfile, srcfs, buildfs):
        buildfs.write(buildfile, srcfs.read(filepath))
        return 'angular/styles', True

    def ng_angular_json(self, build, filepath, buildfile, srcfs, buildfs):
        ng_build_options = srcfs.read.json(filepath)
        angularjson = buildfs.read.json("angular.json", dict())
        for key in ng_build_options:
            if key in ["outputPath", "index", "main", "polyfills", "tsConfig", "inlineStyleLanguage"]: continue
            angularjson["projects"]['build']["architect"]["build"]["options"][key] = ng_build_options[key]
        buildfs.write("angular.json", json.dumps(angularjson, indent=4))
        return 'angular/angular.json', True

class Build(Base):
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
            buildfs.delete("src/styles")

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
                deps = converter.dependencies(text)
                for dep in deps:
                    pkg = deps[dep]
                    component_import = component_import + "\nimport { "+ dep +" } from '" + pkg + "'"
                    ngmodule_imports.append(dep)
        ngmodule_imports = ",\n".join(["        " + x for x in ngmodule_imports])
        
        app_module_ts = srcfs.read(os.path.join("angular", "app", "app.module.ts"))
        app_module_ts = component_import + "\n\n" + app_module_ts
        app_module_ts = converter.syntax(app_module_ts, declarations=component_declarations, imports=ngmodule_imports)
        buildfs.write(os.path.join("src", "app", "app.module.ts"), app_module_ts)

        # run esbuild
        execute(f"cd {buildfs.abspath()} && node wizbuild")
        srcfs.copy(buildfs.abspath("package.json"), os.path.join("angular", "package.json"))
