import season
import pymysql
import json
from werkzeug.exceptions import HTTPException

CODE_FILTER = """request_uri = framework.request.uri()
if request_uri == '/':
    return framework.response.redirect("/wiz")

lang = framework.request.query("lang", None)
if lang is not None:
    lang = lang.upper()
    framework.response.language(lang)
    framework.dic.set_language(framework.request.language())

framework.session = framework.lib.session.to_dict()
framework.response.data.set(session=framework.session)
"""

CODE_BUILD_RESOURCE = """import lesscpy
from six import StringIO

cache = season.cache
if 'resources' not in cache:
    cache.resources = season.stdClass()

_, ext = os.path.splitext(resource_filepath)
filepath = os.path.join(resource_dirpath, resource_filepath)
if filepath in cache.resources:
    return cache.resources[filepath]

if ext == '.less':
    f = open(filepath, 'r')
    lessfile = f.read()
    f.close()
    cssfile = lesscpy.compile(StringIO(lessfile), minify=True)
    response = flask.Response(str(cssfile))
    response.headers['Content-Type'] = 'text/css'
    cache.resources[filepath] = response
    return cache.resources[filepath]
"""

CODE_BUILD = ""

class Controller(season.interfaces.wiz.ctrl.admin.setting.api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def packageinfo(self, framework):
        try:
            fs = framework.model("wizfs", module="wiz").use(".")
            opts = fs.read_json("wiz.json")
        except:
            opts = {}
        package = season.stdClass(opts)

        if 'framework' not in package:
            config = framework.config().load()
            package.framework = {}
            package.framework["host"] = config.get("host", "0.0.0.0")
            package.framework["port"] = config.get("port", "3000")
            package.framework["watch"] = dict()
            try:
                package.framework["watch"]['pattern'] = config.get("watch").pattern
            except:
                package.framework["watch"]['pattern'] = '*'
            try:
                package.framework["watch"]['ignore'] = config.get("watch").ignore
            except:
                package.framework["watch"]['ignore'] = ''
            package.framework["dev"] = config.get("dev", False)

            package.framework["jinja_variable_start_string"] = config.get("jinja_variable_start_string", "{$")
            package.framework["jinja_variable_end_string"] = config.get("jinja_variable_end_string", "$}")
            package.framework["log_level"] = str(config.get("log_level", 2))
            package.framework["on_error"] = "raise err"
            package.framework["build"] = ""
            package.framework["filter"] = CODE_FILTER
            package.framework["build_resource"] = CODE_BUILD_RESOURCE

        if "build" not in package.framework: package.framework["build"] = ""
        if "on_error" not in package.framework: package.framework["on_error"] = "raise err"
        if "filter" not in package.framework: package.framework["filter"] = CODE_FILTER
        if "build_resource" not in package.framework: package.framework["build_resource"] = CODE_BUILD_RESOURCE
        
        framework.response.status(200, package)

    def update(self, framework):
        data = framework.request.query("data", True)
        fs = framework.model("wizfs", module="wiz").use(".")
        fs.write("wiz.json", data)
        framework.response.status(200, True)

    def wizconfigpy(self, package):
        def addtabs(v, size=1):
            for i in range(size):
                v =  "    " + "\n    ".join(v.split("\n"))
            return v

        try:
            if len(package.framework.watch.pattern) == 0:
                package.framework.watch.pattern = "*"
        except:
            pass

        # config/config.py
        configpy = []
        configpy.append(f"import season")
        configpy.append(f"config = season.stdClass()")
        configpy.append(f"")
        configpy.append(f"config.themepath = 'modules/themes'")
        try:
            if package.wiz.theme.default is not None:
                configpy.append(f"config.theme_default = '{package.wiz.theme.default}'")
        except:
            pass
        
        configpy.append(f"")
        configpy.append("config.pug = season.stdClass()")
        configpy.append("config.pug.variable_start_string = '{$'")
        configpy.append("config.pug.variable_end_string = '$}'")
        configpy.append(f"")


        category = package.wiz.category.split("\n")
        makecategory = []
        for cate in category:
            _cate = cate.split(":")
            if len(_cate) == 1:
                _cate[0] = _cate[0].strip()
                makecategory.append({"id": _cate[0], "title": _cate[0]})
            if len(_cate) == 2:
                _cate[0] = _cate[0].strip()
                _cate[1] = _cate[1].strip()
                makecategory.append({"id": _cate[0], "title": _cate[1]})
        category = json.dumps(makecategory)
        configpy.append(f"config.category = {category}")
        configpy.append(f"")

        topmenus = package.wiz.topmenus.split("\n")
        maketopmenus = []
        for topmenu in topmenus:
            _topmenu = topmenu.split(":")
            if len(_topmenu) == 1:
                _topmenu[0] = _topmenu[0].strip()
                maketopmenus.append({"title": _topmenu[0], "url": ""})
            if len(_topmenu) == 2:
                _topmenu[0] = _topmenu[0].strip()
                _topmenu[1] = _topmenu[1].strip()
                maketopmenus.append({"title": _topmenu[0], "url": _topmenu[1]})
        topmenus = json.dumps(maketopmenus)
        configpy.append(f"config.topmenus = {topmenus}")
        configpy.append(f"")

        extmap = {}
        extmap[".py"] = "python"
        extmap[".js"] = "javascript"
        extmap[".ts"] = "typescript"
        extmap[".css"] = "css"
        extmap[".less"] = "less"
        extmap[".sass"] = "scss"
        extmap[".scss"] = "scss"
        extmap[".html"] = "html"
        extmap[".pug"] = "pug"
        extmap[".json"] = "json"
        extmap[".svg"] = "html"

        try:
            supportfiles = package.wiz.supportfile.split("\n")
            for supportfile in supportfiles:
                _supportfile = supportfile.split(":")
                if len(_supportfile) != 2:
                    continue
                ext = _supportfile[0].strip()
                lang = _supportfile[1].strip()
                if lang[0] != ".":
                    lang = "." + lang
                extmap[ext] = lang
        except:
            pass
        extmap = json.dumps(extmap)
        configpy.append(f"config.supportfiles = {extmap}")
        configpy.append(f"")

        code = package.wiz.acl
        configpy.append(code)
        configpy.append("config.acl = acl")
        configpy.append("")

        configpy = "\n".join(configpy)
        return configpy

    def configpy(self, package):
        def addtabs(v, size=1):
            for i in range(size):
                v =  "    " + "\n    ".join(v.split("\n"))
            return v

        try:
            if len(package.framework.watch.pattern) == 0:
                package.framework.watch.pattern = "*"
        except:
            pass

        # config/config.py
        configpy = []
        configpy.append(f"import flask")
        configpy.append(f"import season")
        configpy.append(f"import os")
        configpy.append(f"")
        configpy.append(f"config = season.stdClass()")
        configpy.append(f"")
        configpy.append(f"config.dev = {package.framework.dev}")
        configpy.append(f"config.host = '{package.framework.host}'")
        configpy.append(f"config.port = {package.framework.port}")
        configpy.append(f"config.log_level = {package.framework.log_level}")
        configpy.append(f"")
        configpy.append("config.jinja_variable_start_string = '{$'")
        configpy.append("config.jinja_variable_end_string = '$}'")
        configpy.append(f"")
        configpy.append(f"config.watch = season.stdClass()")

        patterns = package.framework.watch.pattern.replace(' ', '').replace('\t', '')
        patterns = patterns.split("\n")
        patterns = json.dumps(patterns)
        configpy.append(f"config.watch.pattern = {patterns}")

        ignores = package.framework.watch.ignore.replace(' ', '').replace('\t', '')
        ignores = ignores.split("\n")
        ignores = json.dumps(ignores)
        configpy.append(f"config.watch.ignore = {ignores}")

        configpy.append(f"")
        configpy.append(f"config.filter = ['indexfilter']")
        configpy.append(f"")

        # build hanlder
        secret_key = package.framework['secret_key']
        if secret_key is None or len(secret_key) == 0: secret_key = "season-wiz"
        code = package.framework["build"]
        code = code + "\n" + CODE_BUILD
        code = addtabs(code, 2)
        script = "def build(app, socketio):\n"
        script = script + f"    try:\n{code}\n        pass\n    except:\n        pass\n"
        script = script + f"    app.secret_key = '{secret_key}'"
        configpy.append(script)
        configpy.append("config.build = build")
        configpy.append("")

        # error handler
        try:
            code = package.framework["on_error"]
            code = addtabs(code, 1)
            script = "def on_error(framework, err):\n"
            script += code + "\n"
            script += "    pass"
            configpy.append(script)
            configpy.append("config.on_error = on_error")
            configpy.append("")
        except:
            pass

        # before request
        try:
            code = package.framework["before_request"]
            if len(code) > 0:
                code = addtabs(code, 1)
                script = "def before_request():\n"
                script += code + "\n"
                script += "    pass"
                configpy.append(script)
                configpy.append("config.before_request = before_request")
                configpy.append("")
        except:
            pass

        # after request
        try:
            code = package.framework["after_request"]
            if len(code) > 0:
                code = addtabs(code, 2)
                script = "def after_request(response):\n"
                script += f"    try:\n"
                script += code + "\n"
                script += f"    except:\n"
                script += f"        pass\n"
                script += f"    return None\n"
                configpy.append(script)
                configpy.append("config.after_request = after_request")
                configpy.append("")
        except:
            pass

        # resource handler
        try:
            code = package.framework["build_resource"]
            if len(code) > 0:
                code = addtabs(code, 2)
                script  = f"def get_resource_handler(resource_dirpath, resource_filepath):\n"
                script += f"    try:\n"
                script += code + "\n"
                script += f"    except:\n"
                script += f"        pass\n"
                script += f"    return None\n"
                
                configpy.append(script)
                configpy.append("config.build_resource = get_resource_handler")
                configpy.append("")
        except:
            pass
        
        configpy = "\n".join(configpy)
        return configpy

    def apply(self, framework):
        # load wiz config file
        try:
            fs = framework.model("wizfs", module="wiz").use(".")
            package = fs.read_json("wiz.json")
        except:
            package = {}
        package = season.stdClass(package)

        # create filter py
        def addtabs(v, size=1):
            for i in range(size):
                v =  "    " + "\n    ".join(v.split("\n"))
            return v

        filterpy = None
        try:
            code = package.framework.filter
            code = addtabs(code, 2)

            filterpy = []
            filterpy.append(f"def process(framework):")
            filterpy.append(f"    def _process():")
            filterpy.append(code)
            filterpy.append(f'    _process()')

            filtertest = "\n".join(filterpy)
            try:
                _tmp = {'config': None}
                exec(filtertest, _tmp)
                _tmp['process'](framework)
            except season.core.CLASS.RESPONSE.STATUS as e:
                pass
            except HTTPException as e:
                pass
            except Exception as e:
                raise e

            filterpy.append("")
            filterpy.append(f'    framework.wiz = framework.model("wiz", module="wiz")')
            filterpy.append(f'    framework.response.data.set(wiz=framework.wiz)')
            filterpy.append(f'    framework.wiz.route()')
            filterpy.append("")

            filterpy = "\n".join(filterpy)
        except Exception as e:
            framework.response.status(500, str(e))

        # create config.py
        configpy = None
        try:
            configpy = self.configpy(package)
        except Exception as e:
            framework.response.status(500, str(e))

        if configpy is None:
            framework.response.status(500, "wiz.py not created")

        try:
            _tmp = {'config': None}
            exec(configpy, _tmp)
            _tmp['config']
        except Exception as e:
            framework.response.status(500, str(e))


        fs = framework.model("wizfs", module="wiz").use("app/config")
        wizconfigpy = None
        try:
            wizconfigpy = self.wizconfigpy(package)
        except Exception as e:
            framework.response.status(500, str(e))

        if wizconfigpy is None:
            framework.response.status(500, "wiz.py not created")

        try:
            _tmp = {'config': None}
            exec(wizconfigpy, _tmp)
            configtest = _tmp['config']

            try:
                configtest.acl(framework)
            except season.core.CLASS.RESPONSE.STATUS as _:
                pass
            except HTTPException as _:
                pass
            except Exception as e1:
                raise e1
        except Exception as e:
            framework.response.status(500, str(e))

        fs = framework.model("wizfs", module="wiz").use("app/config")
        fs.write("config.py", configpy)
        fs.write("wiz.py", wizconfigpy)
        
        fs = framework.model("wizfs", module="wiz").use("app/filter")
        fs.write("indexfilter.py", filterpy)
        
        framework.response.status(200, True)