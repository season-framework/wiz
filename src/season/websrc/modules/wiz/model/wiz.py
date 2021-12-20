import season
import base64
import json
import os
import datetime
from werkzeug.routing import Map, Rule
import time
import markupsafe
import git
import io

WIZ_JS = """if (!window.season_wiz) {
    window.season_wiz = (() => {
        let obj = {};
        obj.__cache__ = {};

        obj.load = (app_id, namespace, app_namespace, render_id) => {
            let wiz = {};
            wiz.id = app_id;
            wiz.namespace = namespace;
            wiz.app_namespace = app_namespace;
            wiz.render_id = render_id;

            wiz.socket = {};
            wiz.socket.active = false;

            if (window.io) {
                wiz.socket.active = true;
                wiz.socket.get = (socketnamespace) => {
                    let socketns = "/wiz/api/" + app_namespace;
                    if (socketnamespace) socketns = "/wiz/api/" + socketnamespace;
                    if (wiz.branch != 'master') socketns = socketns + "/" + wiz.branch;

                    wiz.socket_instance = window.io(socketns);
                    return wiz.socket_instance;
                }
            }

            wiz.API = {
                url: (fnname) => '/wiz/api/' + app_id + '/' + fnname,
                function: (fnname, data, cb, opts) => {
                    let _url = wiz.API.url(fnname);
                    let ajax = {
                        url: _url,
                        type: 'POST',
                        data: data
                    };

                    if (opts) {
                        for (let key in opts) {
                            ajax[key] = opts[key];
                        }
                    }

                    $.ajax(ajax).always((a, b, c) => {
                        cb(a, b, c);
                    });
                },
                async: (fnname, data, opts = {}) => {
                    const _url = wiz.API.url(fnname);
                    let ajax = {
                        url: _url,
                        type: "POST",
                        data: data,
                        ...opts,
                    };

                    return new Promise((resolve) => {
                        $.ajax(ajax).always(function (a, b, c) {
                            resolve(a, b, c);
                        });
                    });
                }
            };

            wiz.timeout = (timestamp) => new Promise((resolve) => {
                setTimeout(resolve, timestamp);
            });

            wiz._event = {};
            wiz._response = {};
            wiz._response_activator = {};

            wiz.bind = (name, fn) => {
                wiz._event[name] = (data) => new Promise(async (resolve, reject) => {
                    let res = await fn(data);
                    if (res) {
                        return resolve(res);
                    }

                    wiz._response_activator[name] = true;

                    let response_handler = () => {
                        // if not activate, stop loop
                        if (!wiz._response_activator[name]) {
                            reject("deprecated event `" + name + "` of `" + wiz.namespace + "`");
                            return;
                        }

                        // if activate 
                        if (name in wiz._response) {
                            let resp = wiz._response[name];
                            delete wiz._response[name];
                            delete wiz._response_activator[name];
                            resolve(resp);
                            return;
                        }

                        setTimeout(response_handler, 100);
                    }
                    response_handler();
                });
                return wiz;
            };

            wiz.response = (name, data) => {
                if (!wiz._response_activator[name]) return;
                wiz._response[name] = data;
                return wiz;
            }

            wiz.connect = (id) => {
                if (!obj.__cache__[id]) return null;
                let connected_wiz = obj.__cache__[id];
                let _obj = {};

                _obj.event = async (name) => {
                    delete connected_wiz._response_activator[name];
                    await wiz.timeout(200);

                    if (connected_wiz._event[name]) {
                        let res = await connected_wiz._event[name](_obj._data);
                        return res;
                    }
                    return null;
                };

                _obj._data = null;
                _obj.data = (data) => {
                    _obj._data = data;
                    return _obj;
                }
                return _obj;
            }

            obj.__cache__[namespace] = wiz;
            obj.__cache__[app_id] = wiz;

            return wiz;
        }

        return obj;
    })();
}
"""

def addtabs(v, size=1):
    for i in range(size):
        v =  "    " + "\n    ".join(v.split("\n"))
    return v

def spawner(code, namespace, logger, **kwargs):
    fn = {'__file__': namespace, '__name__': namespace, 'print': logger, 'season': season}
    for key in kwargs: fn[key] = kwargs[key]
    exec(compile(code, namespace, 'exec'), fn)
    return fn


"""WIZ Process API
: this function used in wiz interfaces code editors and frameworks.

- log(*args)
- render(target_id, namespace, **kwargs)
- dic(key)
- controller(namespace)
- theme()
- resources(path)
"""

class Config(season.stdClass):
    def __init__(self, name='config'):
        self.name = name

    @classmethod
    def load(self, branch, namespace='config'):
        c = Config(namespace)
        config_path = os.path.join(season.core.PATH.PROJECT, 'branch', branch, 'config', namespace + '.py')
        if os.path.isfile(config_path) == False:
            c.data = dict()
        try:
            with open(config_path, mode="rb") as file:
                _tmp = {'config': None}
                _code = file.read().decode('utf-8')
                exec(_code, _tmp)
                c.data = _tmp['config']
        except Exception as e:
            pass
        return c

    def get(self, key=None, _default=None):
        if key is None:
            return self.data
        if key in self.data:
            return self.data[key]
        return _default

class Wiz(season.stdClass):
    def __init__(self, wiz):
        framework = wiz.framework
        self.__wiz__ = wiz
        
        self.__config__ = dict()
        
        self.flask = framework.flask
        self.socketio = framework.socketio
        self.lib = framework.lib
        self.flask_socketio = framework.flask_socketio

        if 'wiz_instance' not in framework.cache:
            framework.cache.wiz_instance = season.stdClass()
        
        self.cache = CacheControl(wiz, namespace="instance")

        self.PATH = framework.core.PATH
        self.request = framework.request
        self.response = framework.response
        
        self.response.render = self.__render__
        self.render = self.__view__

        self.__logger__ = self.logger("instance")

    def logger(self, tag=None, log_color=94):
        class logger:
            def __init__(self, tag, log_color, wiz):
                self.tag = tag
                self.log_color = log_color
                self.wiz = wiz

            def log(self, *args):
                tag = self.tag
                log_color = self.log_color
                wiz = self.wiz
                
                if tag is None: tag = "undefined"
                tag = "[wiz]" + tag
                
                args = list(args)
                for i in range(len(args)): 
                    args[i] = str(args[i])
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                logdata = f"\033[{log_color}m[{timestamp}]{tag}\033[0m " + " ".join(args)
                print(logdata)

                if self.wiz.is_dev():
                    branch = wiz.__wiz__.branch()
                    wiz.socketio.emit("log", logdata + "\n", namespace="/wiz", to=branch, broadcast=True)
                
        return logger(tag, log_color, self).log

    def __dic__(self, mode, app_id):
        class dic:
            def __init__(self, wizinst, mode, app_id):
                self.__wizinst__ = wizinst
                self.mode = mode
                self.app_id = app_id
                self.cache = dict()
            
            def dic(self, key=None):
                wiz = self.__wizinst__.__wiz__

                if mode is None or app_id is None:
                    return ""

                language = self.__wizinst__.request.language()
                language = language.lower()
                
                if language in self.cache:
                    dic = self.cache[language]
                else:
                    if mode == 'route': 
                        inst = wiz.cls.Route(wiz)
                    else: 
                        inst = wiz.cls.App(wiz)
                    dic = inst.dic(app_id)

                    if language in dic: dic = dic[language]
                    if "default" in dic: dic = dic["default"]
                    self.cache[language] = dic

                if key is None:
                    return dic

                key = key.split(".")
                tmp = dic
                for k in key:
                    if k not in tmp:
                        return ""
                    tmp = tmp[k]

                return tmp

        dicinst = dic(self, mode, app_id)
        return dicinst.dic

    def __render__(self, *args, **kwargs):
        wiz = self.__wiz__
        framework = wiz.framework

        if len(args) == 0:
            return self

        if len(args) == 1:
            view = self.render(*args, **kwargs)
            framework.response.send(view, "text/html")
        
        route = args[0]
        endpoint = args[1]

        if route is None: return self
        if len(route) == 0: return self
        url_map = []
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
        app_id, segment = matcher(request_uri)

        if app_id is None:
            return self

        self.request.segment = season.stdClass(segment)
        view = self.render(app_id, **kwargs)
        framework.response.send(view, "text/html")

    def __compiler__(self, codelang, code, **kwargs):
        branch = self.branch()
        logger = self.logger(f"[compiler][{codelang}]")
        try:
            if code is None: return ""
            if len(code) == 0: return code
            wiz = self.__wiz__
            fs = wiz.framework.model("wizfs", module="wiz").use(f"wiz/branch/{branch}/compiler")
            if fs.isfile(f"{codelang}.py") == False:
                return code
            compiler = fs.read(f"{codelang}.py")
            compiler = spawner(compiler, "season.wiz.compiler", logger, wiz=self)
            return compiler['compile'](self, code, kwargs)
        except Exception as e:
            logger(e)
            raise e

    def is_dev(self):
        return self.__wiz__.is_dev()
    
    def branch(self):
        return self.__wiz__.branch()

    def controller(self, namespace):
        wiz = self.__wiz__
        fs = wiz.storage()
        fsns = fs.namespace
        fsns = os.path.join(fsns, "interfaces/controller")
        fs = fs.use(fsns)
        code = fs.read(namespace + ".py")
        logger = self.logger(f"[controller][{namespace}]", 94)
        obj = spawner(code, 'season.wiz.controller', logger, wiz=self)
        return obj['Controller']

    def config(self, namespace="config"):
        branch = self.branch()
        if branch not in self.__config__: 
            self.__config__[branch] = dict()
        if namespace in self.__config__[branch]: 
            config = self.__config__[branch][namespace]
        else:
            self.__config__[branch][namespace] = config = Config.load(branch, namespace)
        return config

    def model(self, namespace):
        wiz = self.__wiz__
        fs = wiz.storage()
        fsns = fs.namespace
        fsns = os.path.join(fsns, "interfaces/model")
        fs = fs.use(fsns)
        code = fs.read(namespace + ".py")
        logger = self.logger(f"[model][{namespace}]", 94)
        obj = spawner(code, 'season.wiz.model', logger, wiz=self)
        return obj['Model']

    def theme(self, themename, layoutname, viewpath, view=None):
        layout = self.layout(themename, layoutname, viewpath, view=view)
        return layout

    def layout(self, themename, layoutname, viewpath, view=None):
        wiz = self.__wiz__
        framework = wiz.framework
        cache = wiz.cache

        THEME_BASEPATH = os.path.join(wiz.branchpath(), "themes")
        namespace = f"{themename}/layout/{layoutname}/{viewpath}"

        layout = cache.get(f"themes/{namespace}")
        
        if layout is None:
            _, ext = os.path.splitext(viewpath)
            if ext[0] == ".": ext = ext[1:]
            ext = ext.lower()

            fs = wiz.storage().use(THEME_BASEPATH)
            layout = fs.read(namespace)
            layout = self.__compiler__(ext, layout)
            cache.set(f"themes/{namespace}", layout)
        
        kwargs = framework.response.data.get()
        kwargs['wiz'] = self
        if view is not None:
            kwargs['view'] = markupsafe.Markup(view)
        layout = framework.response.template_from_string(layout, **kwargs)
        return markupsafe.Markup(layout)

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

    def __view__(self, *args, **kwargs):
        if len(args) == 0: return ""

        wiz = self.__wiz__
        cache = wiz.cache
        framework = wiz.framework

        app_id = args[0] # app unique id or app namespace

        findindex = app_id
        if len(args) > 1: findindex = args[1]

        # find by namespace and id
        app = cache.get(f"apps/byviewnamespace/{findindex}")
        if app is None: app = cache.get(f"apps/bynamespace/{app_id}")
        if app is None: app = cache.get(f"apps/byid/{app_id}")

        # if cache not exists, find app
        if app is None:
            inst = wiz.cls.App(self.__wiz__)
            app = inst.get(app_id)

            if app is None:
                _logger = self.logger(f"[app][{app_id}]", 91)
                _logger(f"not found")
                return ""

            app_id = app['package']['id']
            app_namespace = app['package']['namespace']
            namespace = str(app_namespace)  # namespace for ui
            if len(args) > 1: namespace = args[1]
            render_id = app['package']['render_id'] = "wiz_" + app_id + "_" + framework.lib.util.randomstring(16)
        
            # compile controller
            controller = app['controller']
            controller = addtabs(controller)
            controller = f"def process(wiz, **kwargs):\n    framework = wiz\n{controller}\n    return kwargs"
            app['controller'] = controller

            # compile codes
            def load_property(key, default=None):
                try:
                    return app['package']['properties'][key]
                except:
                    return default
            
            codelang_html = load_property("html", "pug")
            codelang_css = load_property("css", "scss")
            codelang_js = load_property("js", "javascript")

            compile_args = dict()
            compile_args['app_id'] = app_id
            compile_args['app_namespace'] = app_namespace
            compile_args['namespace'] = namespace
            compile_args['render_id'] = render_id

            # compile to default language
            if codelang_html != 'html': app['html'] = self.__compiler__(codelang_html, app['html'], **compile_args)
            if codelang_css != 'css': app['css'] = self.__compiler__(codelang_css, app['css'], **compile_args)
            if codelang_js != 'javascript': app['js'] = self.__compiler__(codelang_js, app['js'], **compile_args)

            # compile reformat default language 
            app['html'] = self.__compiler__('html', app['html'], **compile_args)
            app['css'] = self.__compiler__('css', app['css'], **compile_args)
            app['js'] = self.__compiler__('javascript', app['js'], **compile_args)

            # save cache
            cache.set(f"apps/byid/{app_id}", app)
            cache.set(f"apps/bynamespace/{app_namespace}", app)
            cache.set(f"apps/byviewnamespace/{namespace}", app)

        app_id = app['package']['id']
        app_namespace = app['package']['namespace']
        namespace = str(app_namespace)  # namespace for ui
        if len(args) > 1: namespace = args[1]
        render_id = app['package']['render_id']

        if self.app_id is None:
            self.app_id = app_id

        render_theme = None
        if 'theme' in kwargs:
            render_theme = kwargs['theme']
            if render_theme not in self.__wiz__.themes():
                render_theme = None
            self.render_theme = render_theme

        if self.render_theme is None:
            if 'theme' in app['package']:
                render_theme = self.render_theme = app['package']['theme']
            else:
                render_theme = self.render_theme = self.__wiz__.framework.config.load("wiz").get("theme_default", None)

        ctrl = None
        if 'controller' in app['package']:
            ctrl = app['package']['controller']
            ctrl = self.controller(ctrl)
            if ctrl is not None:
                ctrl = ctrl()
                ctrl.__startup__(self)

        logger = self.logger(f"[app][{app_namespace}]", 93)
        dic = self.__dic__('app', app_id)
        controllerfn = spawner(app['controller'], 'season.wiz.app', logger, controller=ctrl, dic=dic, wiz=self)
        kwargs = controllerfn['process'](self, **kwargs)
        kwargs['query'] = framework.request.query()
        
        dicstr = dic()
        dicstr = json.dumps(dicstr, default=season.json_default)
        dicstr = dicstr.encode('ascii')
        dicstr = base64.b64encode(dicstr)
        dicstr = dicstr.decode('ascii')

        kwargsstr = json.dumps(kwargs, default=season.json_default)
        kwargsstr = kwargsstr.encode('ascii')
        kwargsstr = base64.b64encode(kwargsstr)
        kwargsstr = kwargsstr.decode('ascii')

        kwargs['wiz'] = self

        view = app['html']
        js = app['js']
        css = app['css']

        view = f'{view}<script type="text/javascript">{js}</script><style>{css}</style>'

        view = framework.response.template_from_string(view, dicstr=dicstr, kwargs=kwargsstr, dic=dic, **kwargs)
        if render_theme is None:
            return markupsafe.Markup(view)

        render_theme = render_theme.split("/")
        themename = render_theme[0]
        layoutname = render_theme[1]

        view = f'<script type="text/javascript">{WIZ_JS}</script>\n{view}'
        view = self.theme(themename, layoutname, 'layout.pug', view=view)

        return markupsafe.Markup(view)


"""Data Management APIs

- get(app_id, mode='app')
- rows(mode='app')
- update(info, mode='app')
- delete(app_id, mode='app')
"""
class DataManager:
    def __init__(self, wiz):
        self.__wiz__ = wiz
    
    def inst(self, mode):
        wiz = self.__wiz__
        if mode == 'route': inst = wiz.cls.Route(wiz)
        else: inst = wiz.cls.App(wiz)
        return inst

    def get(self, app_id, mode='app'):
        wiz = self.__wiz__
        inst = self.inst(mode)
        app = inst.get(app_id)
        return app

    def rows(self, mode='app'):
        wiz = self.__wiz__
        inst = self.inst(mode)
        apps = inst.rows()
        return apps

    def update(self, info, mode='app'):
        wiz = self.__wiz__
        inst = self.inst(mode)
        apps = inst.update(info)
        return apps

    def delete(self, app_id, mode='app'):
        wiz = self.__wiz__
        inst = self.inst(mode)
        inst.delete(app_id)


"""WIZ Cache API
: this class used in local only.

- get(key, default=None)
- set(key, value)
- flush()
"""
class CacheControl:
    def __init__(self, wiz, namespace="render"):
        self.__wiz__ = wiz
        self.namespace = namespace
        self.cache = wiz.framework.cache
        self.enabled = True
        branch = wiz.branch()

        if namespace not in self.cache:
            self.cache[namespace] = season.stdClass()
        if branch not in self.cache[namespace]:
            self.cache[namespace][branch] = season.stdClass()

    def use(self, namespace):
        if namespace[0] == "/":
            namespace = namespace[1:]
        namespace = os.path.join(self.namespace, namespace)
        return CacheControl(self.__wiz__, namespace=namespace)

    def open(self, key, default=None):
        class Cache:
            def __init__(self, ctrl, key, default):
                self.ctrl = ctrl
                self.key = key
                self.default = default
                self.cache = season.stdClass()
            
            def __enter__(self):
                ctrl = self.ctrl
                key = self.key
                default = self.default
                self.cache[key] = ctrl.get(key, default=default)
                return self.cache

            def __exit__(self, type, value, traceback):
                ctrl = self.ctrl
                key = self.key
                val = self.cache[key]
                ctrl.set(key, val)

        return Cache(self, key, default)

    def enable(self, enabled=True):
        self.enabled = enabled
        return self

    def disable(self, disabled=True):
        if disabled:
            self.enabled = False
        else:
            self.enabled = True
        return self

    def fs(self):
        namespace = self.namespace
        wiz = self.__wiz__
        branch = wiz.branch()
        return wiz.framework.model("wizfs", module="wiz").use(f"wiz/cache/{branch}/{namespace}")

    def get(self, key, default=None):
        namespace = self.namespace
        wiz = self.__wiz__
        
        if namespace.split("/")[0] not in ["socket"]:
            if wiz.is_dev() or self.enabled == False:
                return None
        
        branch = wiz.branch()

        if branch in self.cache[namespace]:
            if key in self.cache[namespace][branch]:
                return self.cache[namespace][branch][key]
        try:
            fs = self.fs()
            if fs.isfile(f"{key}.pkl"):
                return fs.read_pickle(f"{key}.pkl")
        except:
            pass
        return default
        
    def set(self, key, value):
        namespace = self.namespace
        wiz = self.__wiz__
        branch = wiz.branch()
        try:
            fs = self.fs()
            fs.write_pickle(f"{key}.pkl", value)
            self.cache[namespace][branch][key] = value
            return True
        except:
            pass
        return False
        
    def flush(self):
        namespace = self.namespace
        wiz = self.__wiz__
        branch = wiz.branch()
        try:
            fs = self.fs()
            fs.remove(".")
        except:
            pass
        self.cache[namespace][branch] = season.stdClass()


class Git:

    def __init__(self, wiz, branch="master", base_branch="master", author=None, reload=False):
        self.branch = branch
        self.wiz = wiz
        self.remote_path = wiz.framework.model("wizfs", module="wiz").use(f"wiz/branch/master").abspath()
        self.fs = wiz.framework.model("wizfs", module="wiz").use(f"wiz/branch/{branch}")
        self.path = self.fs.abspath()

        gitbranchcache = f'git_{branch}'
        gitremotecache = f'git_{base_branch}'

        if gitbranchcache in wiz.framework.cache and reload == False: self.repo = wiz.framework.cache[gitbranchcache]
        else: wiz.framework.cache[gitbranchcache] = self.repo = git.Repo.init(self.path)
        if gitremotecache in wiz.framework.cache and reload == False: self.remote_repo = wiz.framework.cache[gitremotecache]
        else: wiz.framework.cache[gitremotecache] = self.remote_repo = git.Repo.init(self.remote_path)
    
        if author is not None:
            try:
                _author = self.author()
                _author = season.stdClass(_author)
                author = season.stdClass(author)
                if author.name is not None and _author['name'] != author.name:
                    self.repo.config_writer().set_value("user", "name", author.name).release()
                if author.email is not None and _author['email'] != author.email:
                    self.repo.config_writer().set_value("user", "email", author.email).release()
            except:
                pass

        # if not initialized repo, create first commit
        isinit = len(self.repo.heads)
        
        if isinit == 0:
            # if branch is not master, create remote 
            if branch != 'master':
                remote_branches = [h.name for h in self.remote_repo.heads]

                # create origin and fetch master
                origin = self.repo.create_remote('origin', self.remote_path)
                origin.fetch()

                # if branch in remote, checkout directly
                if branch in remote_branches:
                    branch_head = self.repo.create_head(branch, origin.refs[branch])
                    self.repo.head.set_reference(branch_head)
                    branch_head.checkout()
                
                # if branch not in remote, clone from base branch
                else:
                    # if base branch not in remote, base branch to master
                    if base_branch not in remote_branches:
                        base_branch = "master"

                    # checkout base head
                    base_head = self.repo.create_head(branch, origin.refs[base_branch])
                    self.repo.head.set_reference(base_head)
                    base_head.checkout()

                    # new branch
                    branch_head = self.repo.create_head(branch)
                    self.repo.head.set_reference(branch_head)
                    branch_head.checkout()

                    # push to remote
                    self.push()

            # if branch is master, create .gitignore
            else:
                gitignore = wiz.framework.model("wizfs", module="wiz").read("modules/wiz/.gitignore")
                self.fs.write(".gitignore", gitignore)
                self.commit()

    def branches(self):
        return [h.name for h in self.remote_repo.heads]

    def push(self, remote='origin'):
        origin = self.repo.remote(name=remote)
        origin.push(self.branch)

    def pull(self, remote='origin'):
        origin = self.repo.remote(name=remote)
        origin.pull(self.branch)
        if self.branch != 'master':
            origin.pull('master')

    def add(self):
        self.repo.git.add('--all')

    def commit(self, message="init"):
        self.repo.git.add('--all')

        # if not changed any, return
        try:
            if self.changed() == 0:
                return
        except:
            pass
        
        self.repo.index.commit(message)
        if self.branch != 'master':
            self.push()

    def commits(self, max_count=30, skip=0):
        branch = self.branch
        try:
            commits = list(self.repo.iter_commits(branch, max_count=max_count, skip=skip))
            for i in range(len(commits)):
                commits[i] = {
                    "author": commits[i].author.name, 
                    "author_email": commits[i].author.email, 
                    "committer": commits[i].committer.name, 
                    "committer_email": commits[i].committer.email, 
                    "datetime": commits[i].committed_datetime, 
                    "message": commits[i].message,
                    "id": str(commits[i])
                }
        except:
            commits = []
        return commits

    def changed(self):
        return len(self.diff())

    def diff(self, commit=None):
        repo = self.repo
        
        if commit is None:
            repo.git.add('--all')
            src = "index"
            parent = repo.commit()
            diffs = parent.diff(None)
        else:
            commit = repo.commit(commit)
            src = str(commit)
            if len(commit.parents) == 0:
                parent = None
                diffs = []
            else:
                parent = str(commit.parents[0])
                parent = repo.commit(parent)
                diffs = parent.diff(str(commit))
        
        res = []
        for diff in diffs:
            res.append({"change_type": diff.change_type, "parent_path": diff.a_path, "commit_path": diff.b_path, "commit": src, "parent": str(parent)})

        return res

    def file(self, filepath, commit=None):
        # if commit is None, return from file (index)
        if commit is None:
            return self.fs.read(filepath)
            
        # return file from git
        repo = self.repo
        commit = repo.commit(commit)
        targetfile = commit.tree / filepath

        f = io.BytesIO(targetfile.data_stream.read())
        data = f.read().decode('utf-8')
        
        return data

    def author(self):
        author = dict()
        try: author['name'] = self.repo.config_reader().get_value("user", "name")
        except: author['name'] = 'wiz'
        try: author['email'] = self.repo.config_reader().get_value("user", "email")
        except: author['email'] = 'wiz@localhost'
        return author

    def current(self):
        return self.repo.commit()

class Merge(Git):

    def __init__(self, wiz, branch="master", base_branch="master", author=None, **kwargs):
        if branch == base_branch:
            raise Exception("select different branch")

        self.branch = branch
        self.base_branch = base_branch
        self.wiz = wiz
        
        self.fs = fs = wiz.framework.model("wizfs", module="wiz").use(f"wiz/merge/{branch}_{base_branch}")
        path = fs.abspath()

        remote_origin = wiz.framework.model("wizfs", module="wiz").use(f"wiz/branch/master").abspath()
        remote_target = wiz.framework.model("wizfs", module="wiz").use(f"wiz/branch/{branch}").abspath() # src
        remote_base = wiz.framework.model("wizfs", module="wiz").use(f"wiz/branch/{base_branch}").abspath() # dst

        if fs.isdir(remote_origin) == False: raise Exception("master branch not exists")
        if fs.isdir(remote_base) == False: raise Exception(f"{base_branch} branch not exists")
        if fs.isdir(remote_target) == False: raise Exception(f"{branch} branch not exists")

        _git = Git(wiz, branch=base_branch, reload=True)
        _git.add()
        if _git.changed() > 0:
            raise Exception("Uncommited file exist.")
        origin_commit = _git.current().tree

        _git = Git(wiz, branch=branch, reload=True)
        branch_commit = _git.current()
        
        self.repo = repo = git.Repo.init(path)
        self.remote_repo = remote_repo = git.Repo.init(remote_origin)
        
        if author is not None:
            try:
                _author = self.author()
                _author = season.stdClass(_author)
                author = season.stdClass(author)
                if author.name is not None and _author['name'] != author.name:
                    repo.config_writer().set_value("user", "name", author.name).release()
                if author.email is not None and _author['email'] != author.email:
                    repo.config_writer().set_value("user", "email", author.email).release()
            except:
                pass

        # if not initialized repo, create first commit
        isinit = len(repo.heads)
        if isinit == 0:
            origin = repo.create_remote('origin', remote_origin)
            origin.fetch()

            # copy source branch
            branch_head = repo.create_head(branch, origin.refs[branch]) # src
            base_head = repo.create_head(base_branch, origin.refs[base_branch]) # dst
            
            base_head.checkout() # init as base branch
            try:
                repo.git.merge(branch_head)
            except:
                pass

            unmerged_blobs = repo.index.unmerged_blobs()
            for path in unmerged_blobs:
                fs.delete(path)
                fs.copy(os.path.join(remote_target, path), path)

            repo.git.add('--all')
    
    def commit(self, message="init"):
        self.repo.git.add('--all')

        # if not changed any, return
        if self.changed() == 0:
            return
        
        self.repo.index.commit(message)
        self.push()

    def push(self, remote='origin'):
        # push to target
        if self.base_branch != "master":
            origin = self.repo.remote(name=remote)
            origin.push(self.base_branch)
            _git = Git(self.wiz, branch=self.base_branch, reload=True)
            _git.pull()
        else:
            self.remote_repo.heads[self.branch].checkout("-f")
            origin = self.repo.remote(name=remote)
            origin.push(self.base_branch)
            self.remote_repo.heads[self.base_branch].checkout("-f")


"""WIZ MergeWorkspace API
: this class used in wiz framework level.
: this class control branches using git
"""

class MergeWorkspace:
    def __init__(self, wiz):
        self.wiz = wiz
        self.fs = wiz.framework.model("wizfs", module="wiz").use("wiz/merge")
        self.branch = None
        self.base_branch = None
        self._author = None

    def git(self):
        branch = self.branch
        base_branch = self.base_branch
        if branch is None or base_branch is None:
            raise Exception("Merge Error: not defined branches")
        author = self._author
        return Merge(self.wiz, branch=branch, base_branch=base_branch, author=author)

    def branches(self):
        wheads = self.fs.list()
        wheads.sort()
        res = []

        for b in wheads:
            if b not in res:
                b = b.split("_")
                res.append({"from": b[0], "to": b[1]})

        return res
        
    def checkout(self, branch, base_branch, name=None, email=None):
        author = None
        if name is not None and email is not None:
            author = dict()
            author['name'] = name
            author['email'] = email

        self.branch = branch
        self.base_branch = base_branch
        self._author = author
        self.git()
        return self

    def diff(self, commit=None):
        return self.git().diff(commit=commit)

    def file(self, filepath, commit=None):
        return self.git().file(filepath, commit=commit)

    def commit(self, message=""):
        self.git().commit(message=message)

    def commits(self, max_count=30, skip=0):
        return self.git().commits(max_count=30, skip=0)
        
    def changed(self):
        return self.git().changed()

    def delete(self):
        branch = self.branch
        base_branch = self.base_branch
        try:
            fs = self.wiz.framework.model("wizfs", module="wiz").use(f"wiz/merge")
            fs.delete(f"{branch}_{base_branch}")
        except:
            pass

    def author(self):
        return self.git().author()

"""WIZ Workspace API
: this class used in wiz framework level.
: this class control branches using git
"""

class Workspace:
    def __init__(self, wiz):
        self.wiz = wiz
        self.fs = wiz.framework.model("wizfs", module="wiz").use("wiz/branch")
        self.git_origin = self.git("master")

    def git(self, branch=None, base_branch="master", author=None, reload=False):
        if branch is None: branch = self.branch()
        return Git(self.wiz, branch=branch, base_branch=base_branch, author=author, reload=reload)

    def merge(self):
        return MergeWorkspace(self.wiz)

    def branch(self):
        return self.wiz.env.BRANCH

    def branches(self, working=True, status=False, git=False):
        wheads = self.fs.list()
        gheads = self.git_origin.branches()

        wheads.sort()
        gheads.sort()
        
        res = ['master']
        if status:
            wb = ['master']
            gb = ['master']

        if working:
            for b in wheads:
                if b not in res:
                    res.append(b)
                if status:
                    if b not in wb:
                        wb.append(b)

        # add git branches
        if git:
            for b in gheads:
                if b not in res:
                    res.append(b)
                if status:
                    if b not in gb:
                        gb.append(b)

        # branch name only
        if status == False:
            return res

        # with status
        stat = []
        for b in res:
            obj = dict()
            obj['name'] = b
            obj['working'] = b in wb
            obj['git'] = b in gb
            stat.append(obj)

        return stat
        
    def checkout(self, branch, base_branch="master", name=None, email=None, reload=False):
        author = None
        if name is not None and email is not None:
            author = dict()
            author['name'] = name
            author['email'] = email

        self.wiz.env.BRANCH = branch
        self.git(branch=branch, base_branch=base_branch, author=author, reload=reload)
        return self

    def diff(self, branch=None, commit=None):
        if branch is None: branch = self.branch()
        return self.git(branch).diff(commit=commit)

    def file(self, filepath, branch=None, commit=None):
        if branch is None: branch = self.branch()
        return self.git(branch).file(filepath, commit=commit)

    def commit(self, branch=None, message=""):
        if branch is None: branch = self.branch()
        self.git(branch).commit(message=message)

    def commits(self, branch=None, max_count=30, skip=0):
        if branch is None: branch = self.branch()
        return self.git(branch).commits(max_count=30, skip=0)
        
    def changed(self, branch=None):
        if branch is None: branch = self.branch()
        return self.git(branch).changed()

    def delete(self, branch, remote=False):
        if branch == 'master': raise Exception("master branch not allowed removing")
        if branch == self.branch(): raise Exception("working branch not allowed removing")
                
        # remove from remote
        if remote:
            remote_path = self.wiz.framework.model("wizfs", module="wiz").use(f"wiz/branch/master").abspath()
            remote_repo = git.Repo.init(remote_path)
            remote_repo.git.branch("-D", branch)

        # remove working branch
        try:
            fs = self.wiz.framework.model("wizfs", module="wiz").use(f"wiz/branch/{branch}")
            fs.delete()
        except:
            pass

    def author(self, branch=None):
        if branch is None: branch = self.branch()
        return self.git(branch).author()

""" WIZ Model used in framework level
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

        # load config
        self.config = config = framework.config.load("wiz")

        # set storage
        wizsrc = config.get("src", "wiz")
        self.path = season.stdClass()
        self.path.root = wizsrc
        self.path.apps = os.path.join(wizsrc, "apps")
        self.path.cache = os.path.join(wizsrc, "cache")
        
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
        self.cls.Route = framework.lib.app.Route
        self.cls.App = framework.lib.app.App

        framework.modulename = modulename

        self.workspace = Workspace(self)
        self.cache = CacheControl(self)
        self.data = DataManager(self)
        self.instances = []

    def use(self):
        return Model(self.framework)

    """WIZ Configuration API
    : configuration api used in wiz module.

    - set_env(name, value)  :
    - is_dev()              :
    - set_dev(DEVMODE)      :
    - checkout(branch)      :
    - themes()              :
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
        BASEPATH = os.path.join(self.branchpath(), "themes")
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

    def controllers(self):
        try:
            fs = self.storage()
            fsns = fs.namespace
            fsns = os.path.join(fsns, "interfaces/controller")
            fs = fs.use(fsns)
            rows = fs.files(recursive=True)
            ctrls = []
            for row in rows:
                if row[0] == "/": row = row[1:]
                name, ext = os.path.splitext(row)
                if ext == ".py":
                    ctrls.append(name)
            return ctrls
        except:
            pass
        return []

    def branchpath(self, branch=None):
        if branch is None:
            branch = self.branch()
        return f"wiz/branch/{branch}"

    def storage(self, branch=None):
        framework = self.framework
        branchpath = self.branchpath(branch=branch)
        return framework.model("wizfs", module="wiz").use(branchpath)


    """Git API
    : this function used in framework.
    
    - branch(): return current branch
    """

    def branch(self):
        return self.env.BRANCH


    """Process API
    : this function used in framework.
    
    - api(app_id)
    - route()
    """

    def socket(self, app_id, branch=None):
        if branch is None: branch = self.branch()
        self.storage()
        
        app = self.data.get(app_id)
        if app is None or 'socketio' not in app:
            return None

        app_id = app['package']['id']
        namespace = app['package']['namespace']
        socket_api = app['socketio']
        if len(socket_api) == 0:
            return None

        wiz = self.instance()
        wiz.app_id = app_id
        
        namespace = app['package']['namespace']
        logger = wiz.logger(f"[app][{namespace}][socket]")
        dic = wiz.__dic__('app', app_id)
        socketfn = spawner(socket_api, 'season.wiz.app.socket', logger, dic=dic, wiz=wiz)
        return socketfn, wiz

    def api(self, app_id):
        app = self.data.get(app_id)
        if app is None or 'api' not in app:
            return None

        app_id = app['package']['id']
        
        view_api = app['api']
        if len(view_api) == 0:
            return None

        wiz = self.instance()
        wiz.app_id = app_id

        ctrl = None
        if 'controller' in app['package']:
            ctrl = app['package']['controller']
            ctrl = wiz.controller(ctrl)
            if ctrl is not None:
                ctrl = ctrl()
                ctrl.__startup__(wiz)
        
        namespace = app['package']['namespace']
        logger = wiz.logger(f"[app][{namespace}][api]")
        dic = wiz.__dic__('app', app_id)
        apifn = spawner(view_api, 'season.wiz.app.api', logger, controller=ctrl, dic=dic, wiz=wiz)
        return apifn, wiz

    def route(self):
        """select route wiz component and render view.
        this function used in season flask's filter.
        """

        cache = self.cache
        framework = self.framework

        # get request uri
        request_uri = framework.request.uri()

        # ignored for wiz admin interface.
        if request_uri.startswith("/wiz/") or request_uri == '/wiz':
            return

        routes = self.routes()
        app_id, segment = routes(request_uri)

        # if not found, proceed default policy of season flask
        if app_id is None:
            return

        # set segment for wiz component
        framework.request.segment = season.stdClass(segment)
        
        # build controller from route code
        route = cache.get(f"routes/{app_id}")

        if route is None:
            inst = self.cls.Route(self)
            route = inst.get(app_id)
            controller = route['controller']
            controller = addtabs(controller)
            controller = f"def process(wiz):\n    framework = wiz\n{controller}"
            route['controller'] = controller
            cache.set(f"routes/{app_id}", route)
            
        # setup logger
        wiz = self.instance()
        wiz.route_id = app_id

        ctrl = None
        if 'controller' in route['package']:
            ctrl = route['package']['controller']
            ctrl = wiz.controller(ctrl)
            if ctrl is not None:
                ctrl = ctrl()
                ctrl.__startup__(wiz)
        
        logger = wiz.logger(f"[route][{request_uri}]", 93)
        dic = wiz.__dic__('route', app_id)
        controllerfn = spawner(route['controller'], 'season.wiz.route', logger, controller=ctrl, dic=dic, wiz=wiz)
        controllerfn['process'](wiz)


    """WIZ Private API
    : this function used in local only.
    
    - routes(): return all routes
    - instance(): return wiz api object
    """

    def routes(self):
        """load all routes in branch.
        this function used in local only.
        """

        cache = self.cache
        branch = self.branch()

        # load from cache, if `devmode` false
        routes = cache.get("routes")

        # if routes not in cache or `devmode` true, load routes            
        if routes is None:
            inst = self.cls.Route(self)
            rows = inst.rows()
            routes = []
            for row in rows:
                obj = dict()
                obj['route'] = row['package']['route']
                obj['id'] = row['package']['id']
                routes.append(obj)
            cache.set("routes", routes)

        # generate url map
        url_map = []
        for i in range(len(routes)):
            info = routes[i]
            route = info['route']
            if route is None: continue
            if len(route) == 0: continue

            endpoint = info["id"]

            if route == "/":
                url_map.append(Rule(route, endpoint=endpoint))
                continue

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
        
        return matcher

    def instance(self):
        inst = Wiz(self)
        self.instances.append(inst)
        return inst