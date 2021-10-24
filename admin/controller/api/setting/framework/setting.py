import season
from werkzeug.exceptions import HTTPException
import flask
import flask_socketio

build_resource = """cache = season.cache
if 'resources' not in cache:
    cache.resources = season.stdClass()

def build_resource(resource_dirpath, resource_filepath):
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

class Controller(season.interfaces.wiz.admin.api):

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
            package.framework["on_error"] = "def on_error(framework, err):\n    framework.response.redirect('/')"
            package.framework["build"] = "def build(app, socketio):\n    app.debug = True\n    app.secret_key = 'season.wiz'"
            package.framework["build_resource"] = build_resource

        self.status(200, package)

    def update(self, framework):
        data = framework.request.query("data", True)
        fs = framework.model("wizfs", module="wiz").use(".")
        fs.write("wiz.json", data)
        self.status(200, True)

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
        configpy.append(f"config.watch.pattern = '{package.framework.watch.pattern.replace(' ', '')}'")
        configpy.append(f"config.watch.ignore = '{package.framework.watch.ignore.replace(' ', '')}'")
        configpy.append(f"")
        configpy.append(f"config.filter = ['indexfilter']")
        configpy.append(f"")

        # build hanlder
        secret_key = package.framework['secret_key']
        if secret_key is None or len(secret_key) == 0: secret_key = "season-wiz"
        code = package.framework["build"]
        code = addtabs(code, 2)
        script = "def build(app, socketio):\n"
        script = script + f"    try:\n{code}\n    except:\n        pass\n"
        script = script + f"    app.secret_key = '{secret_key}'"
        configpy.append(script)
        configpy.append("config.build = build")
        configpy.append("")

        # error handler
        code = package.framework["on_error"]
        code = addtabs(code, 1)
        script = "def on_error(framework, err):\n"
        script += code + "\n"
        script += "    pass"
        configpy.append(script)
        configpy.append("config.on_error = on_error")
        configpy.append("")

        # resource handler
        code = package.framework["build_resource"]
        code = addtabs(code, 2)
        script  = f"def get_resource_handler():\n"
        script += f"    try:\n"
        script += code + "\n"
        script += f"        return build_resource\n"
        script += f"    except:\n"
        script += f"        pass\n"
        script += f"    return None\n"
        
        configpy.append(script)
        configpy.append("config.build_resource = get_resource_handler()")
        configpy.append("")
        
        configpy = "\n".join(configpy)
        return configpy

    def apply(self, framework):
        try:
            fs = framework.model("wizfs", module="wiz").use(".")
            package = fs.read_json("wiz.json")
        except:
            package = {}
        package = season.stdClass(package)

        def addtabs(v, size=1):
            for i in range(size):
                v =  "    " + "\n    ".join(v.split("\n"))
            return v

        # create filter
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
            self.status(500, str(e))

        # create config.py
        configpy = None
        try:
            configpy = self.configpy(package)
        except Exception as e:
            self.status(500, str(e))

        if configpy is None:
            self.status(500, "wiz.py not created")

        try:
            _tmp = {'config': None}
            exec(configpy, _tmp)
            _tmp['config']
        except Exception as e:
            self.status(500, str(e))

        # update filter
        fs = framework.model("wizfs", module="wiz").use("app/config")
        fs.write("config.py", configpy)
        fs = framework.model("wizfs", module="wiz").use("app/filter")
        fs.write("indexfilter.py", filterpy)

        self.status(200, True)