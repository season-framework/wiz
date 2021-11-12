import season

import base64
import lesscpy
import sass
import dukpy
from six import StringIO
import json
import os
import pypugjs
import datetime
from werkzeug.routing import Map, Rule

RELOADJS = """<script>
function wiz_devtools() {
    try {
        var socket = io("/wiz/devtools/reload/__ID__");
        socket._reload = false;
        socket.on("connect", function () {
            if (socket._reload) {
                location.reload();
            }
        });
        socket.on("reload", function (data) {
            if (data) {
                socket._reload = true;
                return;
            }
            location.reload()
        })
    } catch (e) {
    }
}
wiz_devtools();
</script>
"""
        
class Model:
    def __init__(self, framework):
        wizfs = framework.model("wizfs", module="wiz")
        
        # load package info
        try:
            opts = wizfs.use("modules/wiz").read_json("wiz-package.json")
        except:
            opts = {}
            
        # set variables
        self.package = season.stdClass(opts)
        self.framework = framework 
        self.cache = framework.cache

        # load config
        self.config = config = framework.config.load("wiz")

        # set storage
        wizsrc = config.get("src", "wiz")
        self.path = season.stdClass()
        self.path.root = wizsrc
        self.path.apps = os.path.join(wizsrc, "apps")
        self.path.cache = os.path.join(wizsrc, "cache")

        self.storage = wizfs.use("modules/wiz")
        
        # set Env
        self.env = season.stdClass()
        self.env.DEVTOOLS = config.get("devtools", False)

        try:
            self.env.DEVMODE = framework.request.cookies("season-wiz-devmode", "false")
            if self.env.DEVMODE == "false": self.env.DEVMODE = False
            else: self.env.DEVMODE = True
        except:
            self.env.DEVMODE = False

        try: self.env.BRANCH = framework.request.cookies("season-wiz-branch", "master")
        except: self.env.BRANCH = "master"

        self.cls = season.stdClass()

        modulename = framework.modulename
        framework.modulename = "wiz"
        self.cls.Route = framework.lib.route.Route
        self.cls.App = framework.lib.app.App
        framework.modulename = modulename



    """WIZ Configuration API
    : configuration api used in wiz module.

    - set_env(name, value)  :
    - is_dev()              :
    - set_dev(DEVMODE)      :
    - theme()               :
    """

    def set_env(self, name, value=None):
        if value is None:
            if name in self.env:
                del self.env[name]
        else:
            self.env[name] = value
    
    def is_dev(self):
        return self.env.DEVMODE

    def set_dev(self, DEVMODE):
        """set development mode.
        :param DEVMODE: string variable true/false
        """
        self.framework.response.cookies.set("season-wiz-devmode", DEVMODE)
        if DEVMODE == "false": self.env.DEVMODE = False
        else: self.env.DEVMODE = True

    def themes(self):
        framework = self.framework
        config = framework.config().load('wiz')
        BASEPATH = config.get("themepath", "themes")
        fs = framework.model("wizfs", module="wiz").use(BASEPATH)
        themes = fs.list()
        res = []
        for themename in themes:
            layoutpath = os.path.join(BASEPATH, themename, 'layout')
            fs = fs.use(layoutpath)
            layouts = fs.list()
            for layout in layouts:
                fs = fs.use(os.path.join(layoutpath, layout))
                if fs.isfile('layout.pug'):
                    res.append(f"{themename}/{layout}")
        return res

    # TODO
    def target_version(self):
        if self.env.DEVMODE:
            return "master"
        return "master"

    def commit_id(self, version_name):
        pass


    """WIZ Process API
    : this function used in wiz interfaces code editors and frameworks.

    - render(target_id, namespace, **kwargs)
    - route()
    - theme()
    - resources(path)
    """
    def render(self, *args, **kwargs):
        if len(args) == 0: return ""

        target_id = args[0]

        # if args length is 1, namespace as target_id
        namespace = str(target_id)
        if len(args) > 1: namespace = str(args[1])

        # log trigger
        _prelogger = self.framework.log
        def _logger(*args):
            _prelogger(f"\033[94m[{namespace}]\033[0m", *args)
        self.framework.log = _logger

        # TODO: use cache

        # build source

    def route(self):
        pass


    """Data Management APIs
    - get(target_id)
    - rows()
    - update()
    """

    def get(self, app_id, route=False):
        branch = self.env.BRANCH
        if route: inst = self.cls.Route(self.framework)
        else: inst = self.cls.App(self.framework)
        inst.checkout(branch)
        app = inst.get(app_id)
        return app

    def rows(self, route=False):
        branch = self.env.BRANCH
        if route: inst = self.cls.Route(self.framework)
        else: inst = self.cls.App(self.framework)
        inst.checkout(branch)
        apps = inst.rows()
        return apps

    def update(self, info, route=False):
        branch = self.env.BRANCH
        if route: inst = self.cls.Route(self.framework)
        else: inst = self.cls.App(self.framework)
        inst.checkout(branch)
        apps = inst.update(info)
        return apps

    def delete(self, app_id, route=False):
        branch = self.env.BRANCH
        if route: inst = self.cls.Route(self.framework)
        else: inst = self.cls.App(self.framework)
        inst.checkout(branch)
        inst.delete(app_id)
