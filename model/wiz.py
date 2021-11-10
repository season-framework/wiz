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
        self.path.source = os.path.join(wizsrc, "src")
        self.path.cache = os.path.join(wizsrc, "cache")
        self.path.compiler = os.path.join(wizsrc, "compiler")

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

    """WIZ Configurations
    """
    def set_env(self, name, value=None):
        if value is None:
            if name in self.env:
                del self.env[name]
        else:
            self.env[name] = value

    def target_version(self):
        if self.env.DEVMODE:
            return "master"
        return "master"

    # version tag to git commit
    def commit_id(self, version_name):
        pass

    def is_dev(self):
        return True

    def deploy_version(self):
        return "master"

    """WIZ Process API
    : this function used in wiz interfaces code editors and frameworks.

    - render(target_id, namespace, **kwargs)
    - route()
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
    - search()
    - update()
    - upsert()
    """

    def get(self, target_id):
        target_version = self.target_version()
        target_root = os.path.join(self.path.source, target_id)
        fs = self.storage.use(target_root)

        if fs.isfile("package.wiz") == False:
            return None
        
        def load_property(attr, default=None):
            try:
                return target['properties'][attr]
            except:
                return default

        if 'properties' not in target:
            target['properties'] = dict()

        html = target['properties']["html"] = load_property("html", "pug")
        js = target['properties']["js"] = load_property("js", "js")
        css = target['properties']["css"] = load_property("css", "less")

        target = fs.read_json("package.wiz")
        if 'html' not in target: target["html"] = ""
        if 'js' not in target: target["js"] = ""
        if 'css' not in target: target["css"] = ""

        def load_source(attr, filepath):
            try: target[attr] = fs.read(filepath)
            except: target[attr] = ""

        target["html"] = load_source("html", f"view.{html}")
        target["js"] = load_source("html", f"view.{js}")
        target["css"] = load_source("html", f"view.{css}")

        target["controller"] = load_source("html", f"controller.py")
        target["api"] = load_source("html", f"api.py")
        target["socketio"] = load_source("html", f"socketio.py")

        return target
