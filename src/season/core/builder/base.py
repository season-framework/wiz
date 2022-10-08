import season
import subprocess
from abc import *
import os
import json
import re

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

class Converter:
    def __init__(self, **kwargs):
        self.kwargs = dict(app_id=None, declarations=None, baseuri=None, imports=None)
        for key in kwargs:
            self.kwargs[key] = kwargs[key]

    def angular_component_info(self, code):
        res = dict(inputs=[], outputs=[])
        def convert(match_obj):
            val = match_obj.group(1).replace(" ", "")
            res['inputs'].append(val)
            return val
        pattern = re.compile('@Input\(\)([^=\:\n\;]*)')
        re.sub(pattern, convert, code)
        
        def convert(match_obj):
            val = match_obj.group(1).replace(" ", "")
            res['outputs'].append(val)
            return val
        pattern = re.compile('@Output\(\)([^=\:\n\;]*)')
        re.sub(pattern, convert, code)
        
        return res

    def component_name(self, namespace):
        app_id_split = namespace.split(".")
        componentname = []
        for wsappname in app_id_split:
            componentname.append(wsappname.capitalize())
        componentname = "".join(componentname)
        return componentname
    
    def component_selector(self, namespace):
        return "wiz-" + "-".join(namespace.split("."))

    def directives(self, code):
        result = dict()
        pattern = re.compile('@directives\(([^\)]*)\)', re.DOTALL)
        res = pattern.findall(code)
        for data in res:
            data = data.replace("'", '').replace('"', '').replace(',', '').replace(' ', '')
            pattern = re.compile('(.*):(.*)')
            finded = pattern.findall(data)
            for item in finded:
                result[item[0]] = item[1]
        return result

    def dependencies(self, code):
        result = dict()
        pattern = re.compile('@dependencies\(([^\)]*)\)', re.DOTALL)
        res = pattern.findall(code)
        for data in res:
            data = data.replace("'", '').replace('"', '').replace(',', '').replace(' ', '')
            pattern = re.compile('(.*):(.*)')
            finded = pattern.findall(data)
            for item in finded:
                result[item[0]] = item[1]
        return result
    
    def wrapper(self, fn, code, **kwargs):
        fncall = season.util.fn.call
        try: 
            kwargs['code'] = code
            return fncall(fn, **kwargs)
        except: 
            return code

    def syntax_directives(self, code):
        def convert(match_obj):
            val1 = match_obj.group(1)
            return ""
        pattern = re.compile('@directives\(([^\)]*)\)', re.DOTALL)
        code = re.sub(pattern, convert, code)
        return code

    def syntax_dependencies(self, code):
        def convert(match_obj):
            val1 = match_obj.group(1)
            return ""
        pattern = re.compile('@dependencies\(([^\)]*)\)', re.DOTALL)
        code = re.sub(pattern, convert, code)
        return code

    def syntax_app(self, code):
        def convert(match_obj):
            val = match_obj.group(1)
            if len(val.split("/")) > 1:
                val = val.replace("/directive", "/app.directive")
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

    def syntax_libs(self, code):
        def convert(match_obj):
            val = match_obj.group(1)
            return f'"src/libs/{val}"'
        pattern = r'"@wiz\/libs\/(.*)"'
        code = re.sub(pattern, convert, code)
        pattern = r"'@wiz\/libs\/(.*)'"
        code = re.sub(pattern, convert, code)
        return code

    def syntax_namespace(self, code, app_id):
        if app_id is None: return code
        pattern = r'@wiz.namespace\((.*)\)'
        def convert(match_obj):
            return app_id
        code = re.sub(pattern, convert, code)
        code = code.replace("@wiz.namespace", app_id)
        return code

    def syntax_cwd(self, code, app_id):
        if app_id is None: return code
        def convert(match_obj):
            val = match_obj.group(1)
            val = val.replace("directive", "app.directive")
            return f'"src/app/{app_id}/{val}"'
        pattern = r'"@wiz\/cwd\/(.*)"'
        code = re.sub(pattern, convert, code)
        pattern = r"'@wiz\/cwd\/(.*)'"
        code = re.sub(pattern, convert, code)
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

    def build_params(self, build, srcfs, buildfs, distfs):
        params = season.util.std.stdClass()
        params.build = build
        params.workspace = build.workspace
        params.wiz = build.workspace.wiz
        params.srcfs = srcfs
        params.buildfs = buildfs
        params.distfs = distfs
        return params

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

            if ngtarget in ['app', 'libs', 'wiz.ts']:
                return season.util.fn.call(self.ng_files, buildfile=buildfile, **self.params)

        return None, None

    def app_files(self, filepath, buildfile, srcfs, buildfs):
        buildfs.copy(srcfs.abspath(filepath), buildfile)
        return 'app/files', True

    def app_service_ts(self, wiz, filepath, buildfs, srcfs, segment, converter):
        app_id = segment[1]
        baseuri = self.params.baseuri

        code = srcfs.read(filepath)
        code = f"import Wiz from 'src/wiz';\nlet wiz = new Wiz('{baseuri}').app('{app_id}');\n" + code
        buildfile = os.path.join('src', os.path.dirname(filepath), "service.ts")
        buildfs.write(buildfile, code)
        return 'app/service_ts', True

    def app_view_ts(self, wiz, filepath, buildfs, srcfs, segment, converter):
        appjsonfile = os.path.join(os.path.dirname(filepath), "app.json")
        app_id = segment[1]
        componentname = converter.component_name(app_id)
        appjson = srcfs.read.json(appjsonfile, dict())

        importstr = "import { Component } from '@angular/core';\n"
        baseuri = self.params.baseuri

        # read src code
        code = srcfs.read(filepath)
        code = f"import Wiz from 'src/wiz';\nlet wiz = new Wiz('{baseuri}').app('{app_id}');\n" + code

        # convert syntax
        code = converter.syntax(code, app_id=app_id)

        # convert export class
        component_opts = "{\n    selector: '" + converter.component_selector(app_id) + "',\n    templateUrl: './view.html',\n    styleUrls: ['./view.scss']\n}"
        code = code.replace('export class Component', f"@Component({component_opts})\n" + f'export class {componentname}Component')
        code = f"{importstr}\n" + code.strip()
        code = code + f"\n\nexport default {componentname}Component;"

        buildfile = os.path.join('src', os.path.dirname(filepath), app_id + ".component.ts")
        buildfs.write(buildfile, code)

        try:
            nginfo = converter.angular_component_info(code)
        except:
            nginfo = dict()

        appjson["ng.build"] = dict(id=app_id, name=componentname + "Component", path="./" + app_id + "/" + app_id + ".component")
        ngtemplate = appjson["ng"] = dict(selector=converter.component_selector(app_id), **nginfo)
        
        injector = [f'[{x}]=""' for x in ngtemplate['inputs']] + [f'({x})=""' for x in ngtemplate['outputs']]
        injector = ", ".join(injector)
        appjson['template'] = ngtemplate['selector'] + "(" + injector + ")"
        
        srcfs.write(appjsonfile, json.dumps(appjson, indent=4))

        return 'app/view_ts', True

    def ng_files(self, filepath, buildfile, srcfs, buildfs):
        buildfs.copy(srcfs.abspath(filepath), buildfile)
        return 'angular/files', True

    def ng_app_component(self, wiz, filepath, buildfile, buildfs, srcfs, converter):
        baseuri = self.params.baseuri
        code = srcfs.read(filepath)
        code = f"import Wiz from 'src/wiz';\nlet wiz = new Wiz('{baseuri}');\n" + code
        code = converter.syntax(code)
        buildfs.write(buildfile, code)
        return 'app/app.component.ts', True

    def ng_service(self, filepath, buildfile, srcfs, buildfs):
        code = srcfs.read(filepath)
        buildfs.write(buildfile, code)
        return 'angular/service', True

    def ng_styles(self, filepath, buildfile, srcfs, buildfs):
        buildfs.write(buildfile, srcfs.read(filepath))
        return 'angular/styles', True

    def ng_angular_json(self, build, filepath, buildfile, srcfs, buildfs):
        build_folder = build.config.folder
        ng_build_options = srcfs.read.json(filepath)
        angularjson = buildfs.read.json("angular.json", dict())
        for key in ng_build_options:
            if key in ["outputPath", "index", "main", "polyfills", "tsConfig", "inlineStyleLanguage"]: continue
            angularjson["projects"][build_folder]["architect"]["build"]["options"][key] = ng_build_options[key]
        buildfs.write("angular.json", json.dumps(angularjson, indent=4))
        return 'angular/angular.json', True

class Build(metaclass=ABCMeta):
    def __init__(self, workspace):
        self.workspace = workspace

    def cmd(self, cmd):
        workspace = self.workspace
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        logger = workspace.wiz.logger('[build]')
        if out is not None and len(out) > 0: workspace.wiz.logger('[build][log]')(out.decode('utf-8').strip())
        if err is not None and len(err) > 0: workspace.wiz.logger('[build][error]')(err.decode('utf-8').strip(), level=season.LOG_CRITICAL)

    @abstractmethod
    def event_init(self):
        pass

    @abstractmethod
    def event_build(self):
        pass

    def params(self):
        obj = season.util.std.stdClass()
        obj.season = season
        obj.workspace = self.workspace
        obj.wiz = obj.workspace.wiz
        obj.config = obj.wiz.server.config.build
        
        obj.fs = season.util.std.stdClass()
        obj.fs.workspace = obj.workspace.fs()
        obj.fs.build = obj.workspace.fs(obj.config.folder)
        obj.fs.src = obj.workspace.fs("src")
        obj.fs.dist = obj.workspace.fs("dist")

        obj.workspacefs = obj.fs.workspace
        obj.buildfs = obj.fs.build
        obj.srcfs = obj.fs.src
        obj.distfs = obj.fs.dist

        obj.path = obj.buildfs.abspath()
        obj.cmd = self.cmd
        obj.command = self.cmd
        obj.execute = self.cmd

        return obj

    def __getattr__(self, key):
        params = self.params()
        obj = params[key]
        if hasattr(obj, '__call__'):
            return obj
        def fn():
            return obj
        return fn

    def init(self):
        workspace = self.workspace
        wiz = workspace.wiz
        fn = self.event_init
        params = self.params()
        season.util.fn.call(fn, **params)

    def clean(self):
        workspace = self.workspace
        wiz = workspace.wiz
        buildfs = self.buildfs()
        if buildfs.exists():
            buildfs.delete()
        self.init()

    def __call__(self, filepath=None):
        workspace = self.workspace
        wiz = workspace.wiz
        srcfs = self.srcfs().abspath()
        if filepath is None:
            filepath = ""
        elif filepath.startswith(srcfs):
            filepath = filepath[len(srcfs):]
            if len(filepath) > 0 and filepath[0] == "/":
                filepath = filepath[1:]

        fn = self.event_build
        params = self.params()
        params.filepath = filepath if filepath is not None else ""
        season.util.fn.call(fn, **params)