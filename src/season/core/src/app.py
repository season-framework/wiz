import season
import os
import base64
import json
import datetime
import git
import time
import markupsafe
from werkzeug.routing import Map, Rule
import io

class App:
    def __init__(self, wiz):
        self.wiz = wiz
        self.branch = wiz.branch

    def basepath(self):
        branch = self.branch()
        return os.path.join(season.path.project, "branch", branch, "apps")

    def cachepath(self):
        branch = self.branch()
        return os.path.join(season.path.project, "cache", "branch", branch, "apps")

    def cachefs(self):
        path = self.cachepath()
        fs = season.util.os.FileSystem(path)
        return fs

    def clean(self):
        fs = self.cachefs()
        fs.delete()
    
    def list(self):
        fs = season.util.os.FileSystem(self.basepath())
        routes = fs.files()
        res = []
        for id in routes:
            if fs.isfile(f"{id}/app.json"):
                pkg = self(id)
                res.append(pkg.data(code=False))
        res.sort(key=lambda x: x['package']['id'])
        return res

    def __call__(self, id):
        if id is None: return None
        return self.Package(self, id)

    class Package:
        def __init__(self, manager, id):
            self.manager = manager
            self.fs = season.util.os.FileSystem(os.path.join(manager.basepath(), id))
            self.id = id
            self.memory_id = f'app.{id}'
            self.use_controller = False

        def data(self, code=True):
            wiz = self.manager.wiz
            if self.memory_id in wiz.memory and code is True:
                return wiz.memory[self.memory_id]

            fs = self.fs
            pkg = dict()
            pkg["package"] = fs.read.json(f"app.json")
            def readfile(key, filename, default=""):
                try: pkg[key] = fs.read(filename)
                except: pkg[key] = default
                return pkg

            if code:
                pkg = readfile("controller", "controller.py")
                pkg = readfile("api", "api.py")
                pkg = readfile("socketio", "socketio.py")
                pkg = readfile("html", "html.dat")
                pkg = readfile("js", "js.dat")
                pkg = readfile("css", "css.dat")
                try:
                    pkg['dic'] = fs.read.json("dic.json")
                except:
                    pkg['dic'] = dict()

            wiz.memory[self.memory_id] = pkg
            return pkg

        def dic(self):
            class dicClass:
                def __init__(self, wiz, dicdata):
                    self.wiz = wiz
                    self.dicdata = dicdata

                def __call__(self, key=None):
                    dicdata = self.dicdata
                    language = self.wiz.request.language()
                    language = language.lower()
                    
                    if language in dicdata: dicdata = dicdata[language]
                    elif "default" in dicdata: dicdata = dicdata["default"]
                    
                    if key is None: return dicdata

                    key = key.split(".")
                    tmp = dicdata
                    for k in key:
                        if k not in tmp:
                            return ""
                        tmp = tmp[k]
                    return tmp

            fs = self.fs
            wiz = self.manager.wiz
            dicdata = fs.read.json("dic.json")
            return dicClass(wiz, dicdata)

        def view(self, namespace, **kwargs):
            wiz = self.manager.wiz
            cachefs = season.util.os.FileSystem(os.path.join(self.manager.cachepath(), namespace))

            app_id = self.id
            request_uri = wiz.request.uri()

            data = self.data()

            ctrl = None
            if 'controller' in data['package']:
                ctrl = data['package']['controller']
                ctrl = wiz.controller(ctrl, startup=True)

            logger = wiz.logger(f"[app][{app_id}]", 93)
            dic = self.dic()

            # proceed app controller
            proceed = season.util.os.compiler(data['controller'], name='wiz.app.' + app_id, logger=logger, controller=ctrl, dic=dic, wiz=wiz, kwargs=kwargs)

            dicstr = dic()
            dicstr = json.dumps(dicstr, default=season.util.string.json_default)
            dicstr = dicstr.encode('ascii')
            dicstr = base64.b64encode(dicstr)
            dicstr = dicstr.decode('ascii')

            kwargs = proceed['kwargs']
            kwargs_copy = kwargs.copy()
            kwargsstr = json.dumps(kwargs, default=season.util.string.json_default)
            kwargsstr = kwargsstr.encode('ascii')
            kwargsstr = base64.b64encode(kwargsstr)
            kwargsstr = kwargsstr.decode('ascii')

            # compile view, if not cached
            if cachefs.isfile("compile.pkl"):
                compile_args = cachefs.read.pickle("compile.pkl")
                render_id = compile_args['render_id']
            else:
                render_id = "wiz_" + season.util.string.translate_id(namespace).replace(".", "_") + "_" + season.util.string.random(16)
                compile_args = dict()
                compile_args['app_id'] = app_id
                compile_args['namespace'] = namespace
                compile_args['render_id'] = render_id
                cachefs.write.pickle("compile.pkl", compile_args)

            def load_property(key, default=None):
                try:
                    return data['package']['properties'][key]
                except:
                    return default

            codelang_html = load_property("html", "pug")
            codelang_css = load_property("css", "scss")
            codelang_js = load_property("js", "javascript")

            # check script type (js)
            script_type = 'text/javascript'
            if 'script_type' in data['package']: 
                script_type = data['package']['script_type']

            # compile to default html language
            if cachefs.isfile("view.html"):
                data['html'] = cachefs.read("view.html")
            else:
                if codelang_html != 'html': data['html'] = wiz.compiler(codelang_html).compile(data['html'], **compile_args)
                data['html'] = wiz.compiler('html').compile(data['html'], **compile_args)
                cachefs.write("view.html", data['html'])

            # compile to default css language
            if cachefs.isfile("view.css"):
                data['css'] = cachefs.read("view.css")
            else:
                if codelang_css != 'css': data['css'] = wiz.compiler(codelang_css).compile(data['css'], **compile_args)
                data['css'] = wiz.compiler('css').compile(data['css'], **compile_args)
                cachefs.write("view.css", data['css'])

            if cachefs.isfile("view.js"):
                data['js'] = cachefs.read("view.js")
            else:
                if codelang_js != 'javascript': data['js'] = wiz.compiler(codelang_js).compile(data['js'], **compile_args)
                if script_type == 'text/javascript':
                    data['js'] = wiz.compiler('javascript').compile(data['js'], **compile_args)
                cachefs.write("view.js", data['js'])

            # generate view
            view = data['html']
            js = data['js']
            css = data['css']
            view = f'{view}<script type="{script_type}">{js}</script><style>{css}</style>'
            view = wiz.response.template(view, dicstr=dicstr, kwargs=kwargsstr, dic=dic, wiz=wiz, **kwargs)
            
            return markupsafe.Markup(view)

        def api(self):
            wiz = self.manager.wiz
            app = self.data()
            if app is None or 'api' not in app:
                return None

            app_id = app['package']['id']
            view_api = app['api']
            if len(view_api) == 0:
                return None

            ctrl = None
            if 'controller' in app['package']:
                ctrl = app['package']['controller']
                ctrl = wiz.controller(ctrl, startup=True)
            
            logger = wiz.logger(f"[api][{app_id}]", 93)
            dic = self.dic()
            apifn = season.util.os.compiler(view_api, name='wiz.app.api.' + app_id, logger=logger, controller=ctrl, dic=dic, wiz=wiz)

            return apifn

        def update(self, data):
            # check structure
            required = ['package', 'dic', 'controller', 'api', 'socketio', 'html', 'js', 'css']
            for key in required:
                if key not in data: 
                    raise Exception(f"'`{key}`' not defined")

            required = ['id']
            for key in required:
                if key not in data['package']: 
                    raise Exception(f"'`package.{key}`' not defined")

            # check id format
            id = package['id']
            if len(id) < 4:
                raise Exception(f"id length at least 4")

            allowed = "qwertyuiopasdfghjklzxcvbnm.1234567890"
            for c in id:
                if c not in allowed:
                    raise Exception(f"only alphabet and number and . in package id")

            # update timestamp
            package = data['package']
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if 'created' not in package:
                package['created'] = timestamp
            package['updated'] = timestamp
            data['package'] = package

            # save file
            self.fs.write.json("app.json", data['package'])
            self.fs.write.json("dic.json", data['dic'])
            self.fs.write("controller.py", data['controller'])
            self.fs.write("api.py", data['api'])
            self.fs.write("socketio.py", data['socketio'])
            self.fs.write("html.dat", data['html'])
            self.fs.write("js.dat", data['js'])
            self.fs.write("css.dat", data['css'])

            # update cache
            fs = self.fs
            wiz = self.manager.wiz
            dicdata = fs.read.json("dic.json")

            return self

        def delete(self):
            self.fs.delete()