import season
import json
from werkzeug.exceptions import HTTPException

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

class Controller(season.interfaces.wiz.controller.base):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.framework = framework

    def __default__(self, framework):
        if len(self.config) > 0: framework.response.redirect("/")
        self.js('index.js')
        self.exportjs(request_ip=framework.request.client_ip())
        framework.response.render('index.pug')

    def build(self, framework):
        if len(self.config) > 0: framework.response.status(403)
        data = framework.request.query("data", True)
        fs = framework.model("wizfs", module="wiz").use(".")
        fs.write("wiz.json", data)
        data = json.loads(data)
        data = season.stdClass(data)

        data.framework.on_error = "raise err"
        data.framework.build = ""
        data.framework.build_resource = CODE_BUILD_RESOURCE

        # build config py
        try:
            configpy = self.config_framework(data)
            wizpy = self.config_wiz(data)
            filterpy = self.config_filter(data)
        except:
            framework.response.status(500)

        fs = framework.model("wizfs", module="wiz").use("app/config")
        fs.write("config.py", configpy)
        fs.write("wiz.py", wizpy)

        fs = framework.model("wizfs", module="wiz").use("app/filter")
        fs.write("indexfilter.py", filterpy)


        framework.response.status(200)

    def config_framework(self, package):
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


    def config_wiz(self, package):
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

    def config_filter(self, package):
        framework = self.framework
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
            filterpy.append(f'    framework.wiz = framework.model("wiz", module="wiz").use()')
            filterpy.append(f'    framework.response.data.set(wiz=framework.wiz)')
            filterpy.append(f'    framework.wiz.route()')
            filterpy.append("")

            filterpy = "\n".join(filterpy)
            return filterpy
        except:
            pass
        return None