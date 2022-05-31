import os
import time
from werkzeug.routing import Map, Rule

import season

from season.core.lib.request import request
from season.core.lib.response import response

from season.component.wiz.app import App
from season.component.wiz.route import Route
from season.component.wiz.config import Config
from season.component.wiz.compiler import Compiler
from season.component.wiz.theme import Theme

class wiz(season.util.std.stdClass):
    def __init__(self, server, **kwargs):
        self.server = server
        self.request = request(self)
        self.response = response(self)
        self.route = Route(self)
        self.app = App(self)
        self.compiler = Compiler(self)
        self.theme = Theme(self)
        self.log = self.logger()

        # TODO: cache controller
        self.cache = None

        # deprecated functions
        self.flask = server.flask
        self.socketio = server.flask_socketio
        self.flask_socketio = server.flask_socketio

    def trace(self):
        self.tracer = season.util.std.stdClass()
        self.tracer.branch = self.branch()
        self.tracer.path = self.request.uri()
        self.tracer.log = []
        self.tracer.timestamp = time.time()

        self.memory = season.stdClass()

        self.request = request(self)
        self.response = response(self)

    # TODO: check installed
    def installed(self):
        pass

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
        self.framework.response.cookies.set("season-wiz-devmode", DEVMODE)

    def branch(self, branch=None):
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

        # set branch
        self.response.cookies.set("season-wiz-branch", branch)
        return branch

    def config(self, namespace="config"):
        branch = self.branch()
        c = Config.load(branch, namespace)
        return c

    def model(self, id):
        branch = self.branch()
        path = os.path.join(season.path.project, 'branch', branch, 'interfaces', 'model')
        fs = season.util.os.FileSystem(path)
        code = fs.read(id + ".py")
        logger = self.logger(f"[model][{id}]", 94)
        model = season.util.os.compiler(code, name='wiz.model.' + id, logger=logger, wiz=self)
        return model['Model']

    def controller(self, id, startup=False):
        controller_id = "controller." + id
        if startup is True:
            if controller_id in self.memory:
                return self.memory[controller_id]

        branch = self.branch()
        path = os.path.join(season.path.project, 'branch', branch, 'interfaces', 'controller')
        fs = season.util.os.FileSystem(path)
        code = fs.read(id + ".py")
        logger = self.logger(f"[controller][{id}]", 94)
        ctrl = season.util.os.compiler(code, name='wiz.controller.' + id, logger=logger, wiz=self)
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

    def logger(self, tag=None, log_color=94):
        class logger:
            def __init__(self, tag, log_color, wiz):
                self.tag = tag
                self.log_color = log_color
                self.wiz = wiz

            def log(self, *args, level=season.log.dev, tags=[], color=None):
                tag = self.tag
                if color is None: color = self.log_color
                wiz = self.wiz
                if level < wiz.server.config.server.log_level:
                    return

                if tag is None: tag = ""
                if type(tags) == str:
                    tag = f"[{tags}]{tag}"
                if type(tags) == list:
                    for t in tags: 
                        tag = f"{tag}[{t}]"
                tagmap = ['debug', 'info', 'dev', 'warning', 'error', 'critical']
                
                if level < len(tagmap): tag = "[" + tagmap[level] + "]" + tag
                tag = "[wiz]" + tag

                if wiz.tracer.timestamp is not None:
                    tag = tag + "[" + str(round((time.time() - wiz.tracer.timestamp) * 1000)) + "ms]"
                
                args = list(args)
                for i in range(len(args)): 
                    args[i] = str(args[i])
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                logdata = f"\033[{color}m[{timestamp}]{tag}\033[0m " + " ".join(args)

                print(logdata)
                if self.wiz.is_dev():
                    branch = wiz.branch()
                    wiz.server.socketio.emit("log", logdata + "\n", namespace="/wiz", to=branch, broadcast=True)
                
        return logger(tag, log_color, self).log
