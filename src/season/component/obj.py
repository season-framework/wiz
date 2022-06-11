import os
import time
from werkzeug.routing import Map, Rule
from abc import *

import season

from season.component.wiz.app import App as wiz_app
from season.component.wiz.route import Route as wiz_route
from season.component.wiz.theme import Theme as wiz_theme
from season.component.plugin.app import App as plugin_app
from season.component.plugin.route import Route as plugin_route

import urllib

class Url:
    def __init__(self, wiz):
        self.wiz = wiz
        self.base = wiz.baseurl
        if self.base == '/':
            self.base = ''
    
    def __call__(self, path=""):
        return urllib.parse.urljoin(self.base + "/", path)
    
    def resource(self, path=""):
        return urllib.parse.urljoin(self.base + "/resources/", path)

class InstanceObject(season.util.std.stdClass):
    def __init__(self, server, **kwargs):
        self.server = server
        self.log = self.logger()
        self.cache = season.stdClass()
        self.memory = season.stdClass()
        
        self.__branch__ = None

        self.version = season.version

        self.initialize()
        
        # deprecated functions
        self.flask = server.flask
        self.flask_socketio = server.flask_socketio

        # attach source
        self.src = season.stdClass()
        self.src.app = wiz_app(self)
        self.src.route = wiz_route(self)
        self.src.theme = wiz_theme(self)

        self.src.plugin = season.stdClass()
        self.src.plugin.app = plugin_app(self)
        self.src.plugin.route = plugin_route(self)

        self.url = Url(self)

        wizurl = server.config.server.wiz_url
        if wizurl[-1] == "/": wizurl = wizurl[:-1]
        self.wizurl = wizurl

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def config(self, namespace="config"):
        pass

    @abstractmethod
    def basepath(self):
        pass

    @abstractmethod
    def tag(self):
        pass

    def path(self, *args):
        path = [self.basepath()] + list(args)
        return os.path.join(*path)

    def trace(self):
        self.tracer = season.util.std.stdClass()
        self.tracer.branch = self.branch()
        self.tracer.path = self.request.uri()
        self.tracer.log = []
        self.tracer.timestamp = time.time()

        self.memory = season.stdClass()

        self.initialize()

    def installed(self):
        wiz = self
        if wiz.server.config.installed.started is None:
            install_uri = wiz.wizurl + "/ui/install"
            requri = wiz.request.uri()
            if requri != install_uri:
                wiz.response.redirect(install_uri)
        else:
            install_uri = wiz.wizurl + "/ui/install"
            requri = wiz.request.uri()
            if requri == install_uri:
                wiz.response.redirect(wiz.wizurl)

    def is_dev(self):
        try:
            is_dev = self.request.cookies("season-wiz-devmode", "false")
            if is_dev == "false": is_dev = False
            else: is_dev = True
        except:
            is_dev = False
        branch = self.branch()
        if branch in ['master', 'main']:
            return is_dev
        return True

    def set_dev(self, DEVMODE):
        if DEVMODE == False: DEVMODE = "false"
        if DEVMODE == True: DEVMODE = "true"
        self.response.cookies.set("season-wiz-devmode", DEVMODE)

    def branch(self, branch=None):
        # used not request flow
        if self.__branch__ is not None:
            return self.__branch__

        # find branch
        if branch is None:
            branch = self.request.cookies("season-wiz-branch", "main")
            
            # if branch exists
            branchpath = os.path.join(season.path.project, 'branch', branch)
            if os.path.isdir(branchpath):
                self.response.cookies.set("season-wiz-branch", branch)
                return branch
            
            # if branch not exists, check main
            branch = "main"
            branchpath = os.path.join(season.path.project, 'branch', branch)
            if os.path.isdir(branchpath):
                self.response.cookies.set("season-wiz-branch", branch)
                return branch

            # if branch not exists, check master
            branch = "master"
            branchpath = os.path.join(season.path.project, 'branch', branch)
            if os.path.isdir(branchpath):
                self.response.cookies.set("season-wiz-branch", branch)
                return branch

            # if no branches in project
            raise Exception("branch not found")
        
        else:
            branchpath = os.path.join(season.path.project, 'branch', branch)
            if os.path.isdir(branchpath):
                self.response.cookies.set("season-wiz-branch", branch)
        
        return branch

    def branchpath(self):
        branch = self.branch()
        return os.path.join(season.path.project, 'branch', branch)
    
    def branchfs(self):
        return season.util.os.FileSystem(self.branchpath())

    def branches(self):
        fs = season.util.os.FileSystem(os.path.join(season.path.project, 'branch'))
        return fs.list()

    def model(self, id):
        path = os.path.join(self.basepath(), 'interfaces', 'model')
        fs = season.util.os.FileSystem(path)
        code = fs.read(id + ".py")
        logger = self.logger(f"[model/{id}]", 94)
        model = season.util.os.compiler(code, name=fs.abspath(id + ".py"), logger=logger, wiz=self)
        return model['Model']

    def controller(self, id, startup=False):
        controller_id = "controller." + id
        if startup is True:
            if controller_id in self.memory:
                return self.memory[controller_id]

        path = os.path.join(self.basepath(), 'interfaces', 'controller')
        fs = season.util.os.FileSystem(path)
        code = fs.read(id + ".py")
        logger = self.logger(f"[controller/{id}]", 94)
        ctrl = season.util.os.compiler(code, name=fs.abspath(id + ".py"), logger=logger, wiz=self)
        ctrl = ctrl['Controller']

        if startup is True:
            ctrl = ctrl()
            if hasattr(ctrl, '__startup__'):
                season.util.fn.call(ctrl.__startup__, wiz=self)
            self.memory[controller_id] = ctrl

        return ctrl

    def render(self, *args, **kwargs):
        if len(args) == 0: return ""
        
        # app unique id or app namespace
        id = args[0] 

        # namespace: custom defined id
        namespace = id
        if len(args) > 1: namespace = args[1]

        app = self.app(id)
        view = app.view(namespace, **kwargs)

        return view

    def match(self, route):
        endpoint = "exist"
        url_map = []
        if route == "/":
            url_map.append(Rule(route, endpoint=endpoint))
        else:
            if route[-1] == "/":
                url_map.append(Rule(route[:-1], endpoint=endpoint))
            elif route[-1] == ">":
                rpath = route
                while rpath[-1] == ">":
                    rpath = rpath.split("/")[:-1]
                    rpath = "/".join(rpath)
                    url_map.append(Rule(rpath, endpoint=endpoint))
                    if rpath[-1] != ">":
                        url_map.append(Rule(rpath + "/", endpoint=endpoint))
            url_map.append(Rule(route, endpoint=endpoint))

        url_map = Map(url_map)
        url_map = url_map.bind("", "/")

        def matcher(url):
            try:
                endpoint, kwargs = url_map.match(url, "GET")
                return endpoint, kwargs
            except:
                return None, {}
                
        request_uri = self.request.uri()
        endpoint, segment = matcher(request_uri)
        if endpoint is None:
            return None
        segment = season.stdClass(segment)
        return segment

    def logger(self, tag=None, log_color=94, trace=True):
        class logger:
            def __init__(self, tag, log_color, wiz, trace=True):
                self.tag = tag
                self.log_color = log_color
                self.wiz = wiz
                self.trace = trace

            def log(self, *args, level=season.log.dev, color=None):
                tag = self.tag
                if color is None: color = self.log_color
                wiz = self.wiz
                if level < wiz.server.config.wiz.log_level:
                    return

                if tag is None: tag = ""
                try:
                    if self.trace:
                        if wiz.tracer.code is not None:
                            tag = "[" + str(wiz.tracer.code) + "]" + tag
                        if wiz.tracer.timestamp is not None:
                            tag = "[" + str(round((time.time() - wiz.tracer.timestamp) * 1000)) + "ms]" + tag
                except:
                    pass
                
                tagmap = ['DEBUG', 'INFO', 'WARN', 'DEV', 'ERR', 'CRIT']
                if level < len(tagmap): tag = "[" + tagmap[level] + "]" + tag

                args = list(args)
                for i in range(len(args)): 
                    args[i] = str(args[i])
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                logdata = f"\033[{color}m[{timestamp}]{tag}\033[0m " + " ".join(args)

                print(logdata)
                try:
                    if self.wiz.is_dev():
                        branch = wiz.branch()
                        wiz.server.wsgi.socketio.emit("log", logdata + "\n", namespace="/wiz", to=branch, broadcast=True)
                except:
                    pass
                
        return logger(tag, log_color, self, trace=trace).log
