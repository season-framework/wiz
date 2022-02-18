import season
import json
from werkzeug.exceptions import HTTPException

CODE_BUILD_RESOURCE = """cache = season.cache
if 'resources' not in cache:
    cache.resources = season.stdClass()

_, ext = os.path.splitext(resource_filepath)
filepath = os.path.join(resource_dirpath, resource_filepath)
if filepath in cache.resources:
    return cache.resources[filepath]

ext = ext.lower()

allowed = ['.less', '.scss']
if ext not in allowed:
    return None

if ext == '.less':
    import lesscpy
    from six import StringIO

    f = open(filepath, 'r')
    lessfile = f.read()
    f.close()
    cssfile = lesscpy.compile(StringIO(lessfile), minify=True)
    response = flask.Response(str(cssfile))
    response.headers['Content-Type'] = 'text/css'
    cache.resources[filepath] = response
    return cache.resources[filepath]

if ext == '.scss':
    import sass
    f = open(filepath, 'r')
    css = f.read()
    f.close()
    css = sass.compile(string=css)
    css = str(css)
    response = flask.Response(css)
    response.headers['Content-Type'] = 'text/css'
    cache.resources[filepath] = response
    return cache.resources[filepath]
"""

CODE_AFTER_REQUEST = """response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
response.headers["Pragma"] = "no-cache"
response.headers["Expires"] = "0"
response.headers['Cache-Control'] = 'public, max-age=0'
"""

class Model:
    def __init__(self, framework):
        self.framework = framework
        self.fs = framework.model("wizfs", module="wiz").use("wiz")
    
    def __addtabs__(self, v, size=1):
        for i in range(size):
            v =  "    " + "\n    ".join(v.split("\n"))
        return v

    def get(self):
        framework = self.framework
        fs = self.fs
        access_ip = framework.request.client_ip()

        try:
            opts = fs.read_json("wiz.json")
        except:
            opts = dict()

        package = season.stdClass(opts)
        config = framework.config().load()

        if 'framework' not in package: package.framework = {}
        if "host" not in package.framework: package.framework["host"] = config.get("host", "0.0.0.0")
        if "port" not in package.framework: package.framework["port"] = config.get("port", "3000")
        if "log_level" not in package.framework: package.framework["log_level"] = str(config.get("log_level", 2))
        if "secret_key" not in package.framework: package.framework["secret_key"] = str(config.get("secret_key", 'season-wiz'))
        if "build" not in package.framework: package.framework["build"] = ""
        if "on_error" not in package.framework: package.framework["on_error"] = "raise err"
        if "build_resource" not in package.framework: package.framework["build_resource"] = CODE_BUILD_RESOURCE
        if "before_request" not in package.framework: package.framework["before_request"] = ""
        if "after_request" not in package.framework: package.framework["after_request"] = CODE_AFTER_REQUEST

        if 'wiz' not in package: package.wiz = {}
        if 'category' not in package.wiz: package.wiz['category'] = "component: Component\nwidget: Widget\nmodal: Modal"
        if 'topmenus' not in package.wiz: package.wiz['topmenus'] = "HOME: /\nWIZ: /wiz"
        if 'acl' not in package.wiz: package.wiz['acl'] = f"def acl(framework):\n    req_ip = framework.request.client_ip()\n    if req_ip not in ['127.0.0.1', '{access_ip}']:\n        framework.response.abort(401)"
        if 'supportfile' not in package.wiz: package.wiz['supportfile'] = ".txt: text\n.map: json"
        if 'theme' not in package.wiz: package.wiz['theme'] = dict()

        return package

    def update(self, data):
        framework = self.framework
        fs = self.fs
        fs.write("wiz.json", data)
        
    def build_config(self):
        framework = self.framework
        fs = self.fs
        package = self.get()
        
        configpy = []
        configpy.append(f"import flask")
        configpy.append(f"import season")
        configpy.append(f"import os")
        configpy.append(f"import traceback")
        configpy.append(f"import time")
        configpy.append(f"")
        configpy.append(f"config = season.stdClass()")
        configpy.append(f"")
        configpy.append(f"config.dev = True")
        configpy.append(f"config.host = '{package.framework.host}'")
        configpy.append(f"config.port = {package.framework.port}")
        configpy.append(f"config.log_level = {package.framework.log_level}")
        configpy.append(f"")
        configpy.append("config.jinja_variable_start_string = '{$'")
        configpy.append("config.jinja_variable_end_string = '$}'")
        configpy.append(f"")

        configpy.append(f"")
        configpy.append(f"config.filter = ['indexfilter']")
        configpy.append(f"")

        secret_key = package.framework['secret_key']
        if secret_key is None or len(secret_key) == 0: secret_key = "season-wiz"
        code = package.framework["build"]
        code = code + "\n"
        code = self.__addtabs__(code, 2)
        script = "def build(app, socketio):\n"
        script = script + f"    try:\n{code}\n        pass\n    except:\n        pass\n"
        script = script + f"    app.secret_key = '{secret_key}'"
        configpy.append(script)
        configpy.append("config.build = build")
        configpy.append("")

        try:
            code = package.framework["on_error"]
            code = self.__addtabs__(code, 2)
            script = "def on_error(framework, err):\n"
            script += "    try:\n"
            script += '        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())\n'
            script += '        errorlog = f"\\033[91m[" + timestamp + "}][wiz][error]\\n" + traceback.format_exc() + "\\033[0m"\n'
            script += '        branch = framework.wiz.branch()\n'
            script += '        framework.socketio.emit("log", errorlog, namespace="/wiz", to=branch, broadcast=True)\n'
            script += "    except:\n"
            script += "        pass\n"
            script += "    wiz = framework.wiz.instance()\n"
            script += "    def handle_error(wiz, err):\n"
            script += code + "\n"
            script += "        pass\n"
            script += "    handle_error(wiz, err)\n"
            configpy.append(script)
            configpy.append("config.on_error = on_error")
            configpy.append("")
        except:
            pass

        # before request
        try:
            code = package.framework["before_request"]
            if len(code) > 0:
                code = self.__addtabs__(code, 1)
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
                code = self.__addtabs__(code, 2)
                script = "def after_request(response):\n"
                script += f"    try:\n"
                script += code + "\n"
                script += f"    except:\n"
                script += f"        pass\n"
                script += f"    return response\n"
                configpy.append(script)
                configpy.append("config.after_request = after_request")
                configpy.append("")
        except:
            pass

        # resource handler
        try:
            code = package.framework["build_resource"]
            if len(code) > 0:
                code = self.__addtabs__(code, 2)
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

        # check syntax error
        try:
            _tmp = {'config': None}
            exec(configpy, _tmp)
            configtest = _tmp['config']
        except Exception as e:
            raise e

        return configpy
    
    def build_wiz(self):
        framework = self.framework
        fs = self.fs
        package = self.get()

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

        # check syntax error
        try:
            _tmp = {'config': None}
            exec(configpy, _tmp)
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
            raise e

        return configpy