import season
import pymysql
import json
from werkzeug.exceptions import HTTPException

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
        configpy.append(f"import season")
        configpy.append(f"config = season.stdClass()")
        configpy.append(f"")
        configpy.append(f"config.devtools = {package.wiz.devtools}")
        configpy.append(f"config.themepath = 'modules/themes'")
        try:
            if package.wiz.theme.default is not None:
                configpy.append(f"config.theme_default = '{package.wiz.theme.default}'")
        except:
            pass
        configpy.append(f"")
        configpy.append(f"config.database = season.stdClass()")
        configpy.append(f"config.database.type = 'mysql'")
        configpy.append(f"config.database.host = '{package.wiz.database.host}'")
        configpy.append(f"config.database.port = {package.wiz.database.port}")
        configpy.append(f"config.database.user = '{package.wiz.database.user}'")
        configpy.append(f"config.database.password = '{package.wiz.database.password}'")
        configpy.append(f"config.database.database = '{package.wiz.database.database}'")
        configpy.append(f"config.database.charset = '{package.wiz.database.charset}'")
        configpy.append(f"config.database.prefix = '{package.wiz.database.prefix}'")
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

        code = package.wiz.uid
        configpy.append(code)
        configpy.append("config.uid = uid")
        configpy.append("")

        code = package.wiz.acl
        configpy.append(code)
        configpy.append("config.acl = acl")
        configpy.append("")

        configpy = "\n".join(configpy)
        return configpy

    def connect_test(self, framework):
        config = framework.request.query()
        config = season.stdClass(config)
        dbconfig = season.stdClass()
        dbconfig.host = config.host
        dbconfig.port = int(config.port)
        dbconfig.user = config.user
        dbconfig.password = config.password
        dbconfig.charset = config.charset
        dbconfig.database = config.database
        tablename = config.prefix

        err = None
        rows = []
        try:
            con = pymysql.connect(**dbconfig)
            cursor = con.cursor(pymysql.cursors.DictCursor)
            cursor.execute(f"SHOW CREATE TABLE `{tablename}`")
            rows = cursor.fetchall()
            rows = rows[0]
        except Exception as e:
            err = e
        if err is not None:  
            self.status(500, err)
        self.status(200, rows)

    def apply(self, framework):        
        try:
            fs = framework.model("wizfs", module="wiz").use(".")
            package = fs.read_json("wiz.json")
        except:
            package = {}
        package = season.stdClass(package)

        fs = framework.model("wizfs", module="wiz").use("app/config")
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
            configtest = _tmp['config']

            try:
                configtest.uid(framework)
            except Exception as e1:
                raise e1

            try:
                configtest.acl(framework)
            except season.core.CLASS.RESPONSE.STATUS as _:
                pass
            except HTTPException as _:
                pass
            except Exception as e1:
                raise e1
        except Exception as e:
            self.status(500, str(e))

        fs.write("wiz.py", configpy)
        self.status(200, True)