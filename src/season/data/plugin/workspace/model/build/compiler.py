import season
import os
import json

Annotation = wiz.model("workspace/build/annotation")
Namespace = wiz.model("workspace/build/namespace")
Syntax = wiz.model("workspace/build/syntax")

class Model:
    def __init__(self, builder):
        self.builder = builder

    def fileinfo(self, filepath):
        obj = season.util.std.stdClass()
        obj.root = self.builder.path()
        obj.filepath = filepath
        obj.namespace = os.path.join(*filepath.split("/")[2:])
        obj.basename = os.path.basename(filepath)
        obj.extension = os.path.splitext(filepath)[-1]
        obj.mode = obj.namespace.split("/")[0]
        return obj

    def source(self, filepath):
        fileinfo = self.fileinfo(filepath)
        if fileinfo.extension in ['.pug']:
            return None

        fs = self.builder.fs()

        if fileinfo.mode == 'app':
            fileinfo.app_id = fileinfo.namespace.split("/")[1]
            
            if fileinfo.basename == 'view.ts':
                # compile component file
                fileinfo.code = fs.read(fileinfo.filepath)
                fileinfo.baseuri = self.builder.baseuri()

                importString = "import { Component } from '@angular/core';\n"
                componentName = Namespace.componentName(fileinfo.app_id)
                componentOpts = "{\n    selector: '" + Namespace.selector(fileinfo.app_id) + "',\n    templateUrl: './view.html',\n    styleUrls: ['./view.scss']\n}"

                fileinfo.code = f"import Wiz from 'src/wiz';\nlet wiz = new Wiz('{fileinfo.baseuri}').app('{fileinfo.app_id}');\n" + fileinfo.code
                fileinfo.code = fileinfo.code.replace('export class Component', f"@Component({componentOpts})\n" + f'export class {componentName}Component')
                fileinfo.code = f"{importString}\n" + fileinfo.code.strip()
                fileinfo.code = fileinfo.code + f"\n\nexport default {componentName}Component;"

                targetpath = os.path.join("build/src/app", fileinfo.app_id, fileinfo.app_id + ".component.ts")
                fs.write(targetpath, fileinfo.code)

                self.typescript(targetpath, app_id=fileinfo.app_id)

                # update app.json to source
                appjsonpath = os.path.dirname(fileinfo.filepath)
                appjsonpath = os.path.join(appjsonpath, "app.json")
                appjson = fs.read.json(appjsonpath, dict())
                appjsonpath = "/".join(appjsonpath.split("/")[1:])
                if 'path' in appjson:
                    appjsonpath = appjson['path']
                    del appjson['path']

                appjson = fs.read.json(appjsonpath, dict())
                componentInfo = Annotation.definition.ngComponentDesc(fileinfo.code)
                appjson["ng.build"] = dict(id=fileinfo.app_id, name=componentName + "Component", path="./" + fileinfo.app_id + "/" + fileinfo.app_id + ".component")
                ngtemplate = appjson["ng"] = dict(selector=Namespace.selector(fileinfo.app_id), **componentInfo)
                injector = [f'[{x}]=""' for x in ngtemplate['inputs']] + [f'({x})=""' for x in ngtemplate['outputs']]
                injector = ", ".join(injector)
                appjson['template'] = ngtemplate['selector'] + "(" + injector + ")"
                
                if appjsonpath.split("/")[0] == 'portal':
                    appjson['mode'] = 'portal'
                    appjson['id'] = appjson['namespace']
                
                fs.write(appjsonpath, json.dumps(appjson, indent=4))
                return True

            elif fileinfo.basename in ['view.html', 'view.scss', 'api.py', 'socket.py']:
                if fs.exists(os.path.join("build/src/app", fileinfo.app_id)) == False:
                    fs.makedirs(os.path.join("build/src/app", fileinfo.app_id))
                fs.copy(fileinfo.filepath, os.path.join("build/src/app", fileinfo.app_id, fileinfo.basename))
                return True

            return None

        if fileinfo.mode == 'angular':
            fileinfo.target = fileinfo.namespace.split("/")[1]

            if fileinfo.target == 'styles':
                targetpath = "/".join(fileinfo.namespace.split("/")[2:])
                targetpath = os.path.join("build/src", targetpath)
                targetdir = os.path.dirname(targetpath)
                if fs.isdir(targetdir) == False:
                    fs.makedirs(targetdir)
                fs.copy(fileinfo.filepath, targetpath)
                return True

            if fileinfo.target == 'app':
                targetpath = "/".join(fileinfo.namespace.split("/")[1:])
                targetpath = os.path.join("build/src", targetpath)
                targetdir = os.path.dirname(targetpath)
                if fs.isdir(targetdir) == False:
                    fs.makedirs(targetdir)

                if fileinfo.basename == 'app.component.ts':
                    fileinfo.baseuri = self.builder.baseuri()
                    fileinfo.code = fs.read(fileinfo.filepath)
                    fileinfo.code = f"import Wiz from 'src/wiz';\nlet wiz = new Wiz('{fileinfo.baseuri}');\n" + fileinfo.code
                    fs.write(targetpath, fileinfo.code)
                    self.typescript(targetpath)
                    return True
            
            if fileinfo.target in ['app', 'libs', 'wiz.ts', 'index.html']:
                targetpath = "/".join(fileinfo.namespace.split("/")[1:])
                targetpath = os.path.join("build/src", targetpath)
                targetdir = os.path.dirname(targetpath)
                if fs.isdir(targetdir) == False:
                    fs.makedirs(targetdir)
                fs.copy(fileinfo.filepath, targetpath)
                return True

            if fileinfo.target == 'angular.json':
                angularJson = fs.read.json(fileinfo.filepath, dict())
                angularBuildOptionsJson = os.path.join(os.path.dirname(fileinfo.filepath), "angular.build.options.json")
                if fs.exists(angularBuildOptionsJson):
                    angularBuildOptionsJson = fs.read.json(angularBuildOptionsJson, dict())
                    for key in angularBuildOptionsJson:
                        if key in ["outputPath", "index", "main", "polyfills", "tsConfig", "inlineStyleLanguage"]: continue
                        angularJson["projects"]["build"]["architect"]["build"]["options"][key] = angularBuildOptionsJson[key]

                fs.write("build/angular.json", json.dumps(angularJson, indent=4))
                return True

            if fileinfo.target == 'environment.ts':
                fs.makedirs("build/environments")
                fs.copy(fileinfo.filepath, "build/environments/environment.ts")
                return True

            if fileinfo.target in 'main.ts':
                fs.copy(fileinfo.filepath, "build/src/main.ts")

        return None

    def typescript(self, filepath, **kwargs):
        fileinfo = self.fileinfo(filepath)
        for key in kwargs:
            fileinfo[key] = kwargs[key]

        fs = self.builder.fs()

        fileinfo.baseuri = self.builder.baseuri()
        fileinfo.code = fs.read(fileinfo.filepath)

        if fileinfo.prefix is not None:
            fileinfo.code = fileinfo.prefix + "\n\n" + fileinfo.code
        
        if fileinfo.fnWizRoutes is not None:
            fileinfo.code = fileinfo.code.replace("wiz.routes()", fileinfo.fnWizRoutes)

        fileinfo = Annotation.injection.app(fileinfo)
        fileinfo = Annotation.injection.libs(fileinfo)
        fileinfo = Annotation.injection.namespace(fileinfo)
        fileinfo = Annotation.injection.cwd(fileinfo)
        fileinfo = Annotation.injection.baseuri(fileinfo)
        fileinfo = Annotation.injection.dependencies(fileinfo)
        fileinfo = Annotation.injection.directives(fileinfo)
        fileinfo = Annotation.injection.declarations(fileinfo)
        fileinfo = Annotation.injection.imports(fileinfo)

        fs.write(fileinfo.filepath, fileinfo.code)
        return True
