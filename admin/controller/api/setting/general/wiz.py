import season


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
        script = "def on_error(framework, e):\n"
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
        self.status(200, True)
        
        try:
            fs = framework.model("wizfs", module="wiz").use(".")
            package = fs.read_json("wiz.json")
        except:
            package = {}
        package = season.stdClass(package)

        fs = framework.model("wizfs", module="wiz").use("app/config")
        try:
            configpy = self.configpy(package)
            fs.write("config.py", configpy)
        except Exception as e:
            self.status(500, str(e))
        
        self.status(200, True)