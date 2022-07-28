import season
import os
import base64
import json
import datetime
import markupsafe
from abc import *

class App(metaclass=ABCMeta):
    def __init__(self, wiz):
        self.wiz = wiz
        self.branch = wiz.branch

    @abstractmethod
    def basepath(self):
        pass

    @abstractmethod
    def cachepath(self):
        pass

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

    def cachefs(self):
        path = self.cachepath()
        fs = season.util.os.FileSystem(path)
        return fs

    def clean(self):
        fs = self.cachefs()
        fs.delete()
    
    def load(self, id):
        if id is None: return None
        return self.Package(self, id)

    def __call__(self, id):
        return self.load(id)

    class Package:
        def __init__(self, manager, id):
            self.manager = manager
            self.fs = season.util.os.FileSystem(os.path.join(manager.basepath(), id))
            self.id = id
            self.memory_id = f'app.{id}'

        def data(self, code=True):
            wiz = self.manager.wiz
            if self.memory_id in wiz.memory and code is True:
                return wiz.memory[self.memory_id]

            fs = self.fs
            pkg = dict()
            pkg["package"] = fs.read.json(f"app.json")
            pkg["package"]['id'] = self.id
            
            def load_property(key, default=None):
                try:
                    return pkg['package']['properties'][key]
                except:
                    return default
            codelang_html = load_property("html", "pug")
            codelang_css = load_property("css", "scss")
            codelang_js = load_property("js", "javascript")
            jsmap = {"javascript": "js", "typescript": "ts"}
            codelang_js = jsmap[codelang_js]

            if 'controller' not in pkg['package']: pkg['package']['controller'] = ''
            if 'theme' not in pkg['package']: pkg['package']['theme'] = ''

            def readfile(key, filename, default=""):
                try: pkg[key] = fs.read(filename)
                except: pkg[key] = default
                return pkg

            if code:
                pkg = readfile("controller", "controller.py")
                pkg = readfile("api", "api.py")
                pkg = readfile("socketio", "socketio.py")
                
                if fs.isfile(f"view.{codelang_html}"): pkg["html"] = fs.read(f"view.{codelang_html}")
                elif fs.isfile("html.dat"): pkg["html"] = fs.read("html.dat")
                else: pkg["html"] = ""

                if fs.isfile(f"view.{codelang_js}"): pkg["js"] = fs.read(f"view.{codelang_js}")
                elif fs.isfile("js.dat"): pkg["js"] = fs.read("js.dat")
                else: pkg["js"] = ""

                if fs.isfile(f"view.{codelang_css}"): pkg["css"] = fs.read(f"view.{codelang_css}")
                elif fs.isfile("css.dat"): pkg["css"] = fs.read("css.dat")
                else: pkg["css"] = ""

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
            try:
                dicdata = fs.read.json("dic.json")
            except:
                dicdata = dict()
            return dicClass(wiz, dicdata)

        def view(self, namespace, **kwargs):
            wiz = self.manager.wiz

            respdata = wiz.response.data.get()
            for key in respdata:
                if key not in kwargs:
                    kwargs[key] = respdata[key]

            cachefs = season.util.os.FileSystem(os.path.join(self.manager.cachepath(), namespace))

            app_id = self.id
            request_uri = wiz.request.uri()

            # clean data
            if self.memory_id in wiz.memory:
                del wiz.memory[self.memory_id]
            data = self.data()

            ctrl = None
            if 'controller' in data['package'] and len(data['package']['controller']) > 0:
                ctrl = data['package']['controller']
                ctrl = wiz.controller(ctrl, startup=True)

            tag = wiz.tag()
            logger = wiz.logger(f"[{tag}/app/{app_id}]", 94)
            dic = self.dic()

            # proceed app controller
            name = os.path.join(wiz.basepath(), 'apps', app_id, 'controller.py')
            proceed = season.util.os.compiler(data['controller'], name=name, logger=logger, controller=ctrl, dic=dic, wiz=wiz, kwargs=kwargs)

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
                data['js'] = wiz.compiler('javascript').compile(data['js'], **compile_args)
                cachefs.write("view.js", data['js'])

            # generate view
            view = data['html']
            js = data['js']
            css = data['css']
            view = f'{view}<script type="text/javascript">{js}</script><style>{css}</style>'
            
            filename = os.path.join(wiz.basepath(), 'apps', app_id, f'view.{codelang_html}')
            kwargs['filename'] = filename
            kwargs['kwargs'] = kwargsstr
            kwargs['dicstr'] = dicstr
            kwargs['dic'] = dic
            kwargs['wiz'] = wiz
            view = wiz.response.template(view, **kwargs)
            
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
            if 'controller' in app['package'] and len(app['package']['controller']) > 0:
                ctrl = app['package']['controller']
                ctrl = wiz.controller(ctrl, startup=True)
            
            tag = wiz.tag()
            logger = wiz.logger(f"[{tag}/app/{app_id}/api]", 94)
            dic = self.dic()
            name = os.path.join(wiz.basepath(), 'apps', app_id, 'api.py')
            apifn = season.util.os.compiler(view_api, name=name, logger=logger, controller=ctrl, dic=dic, wiz=wiz)

            return apifn

        def update(self, data):
            # check structure
            required = ['package', 'dic', 'controller', 'api', 'socketio', 'html', 'js', 'css']
            for key in required:
                if key not in data: 
                    raise Exception(f"'`{key}`' not defined")
                elif type(data[key]) is str:
                    data[key] = data[key].replace('', '')

            required = ['id']
            for key in required:
                if key not in data['package']: 
                    raise Exception(f"'`package.{key}`' not defined")

            package = data['package']

            # check id format
            id = package['id']
            if len(id) < 3:
                raise Exception(f"id length at least 3")

            allowed = "qwertyuiopasdfghjklzxcvbnm.1234567890"
            for c in id:
                if c not in allowed:
                    raise Exception(f"only alphabet and number and . in package id")

            # update timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if 'created' not in package:
                package['created'] = timestamp
            package['updated'] = timestamp
            data['package'] = package

            # extensions
            def load_property(key, default=None):
                try:
                    return data['package']['properties'][key]
                except:
                    return default
            codelang_html = load_property("html", "pug")
            codelang_css = load_property("css", "scss")
            codelang_js = load_property("js", "javascript")
            jsmap = {"javascript": "js", "typescript": "ts"}
            codelang_js = jsmap[codelang_js]

            # save file
            self.fs.write.json("app.json", data['package'])
            self.fs.write.json("dic.json", data['dic'])
            self.fs.write("controller.py", data['controller'])
            self.fs.write("api.py", data['api'])
            self.fs.write("socketio.py", data['socketio'])
            self.fs.write(f"view.{codelang_html}", data['html'])
            self.fs.write(f"view.{codelang_js}", data['js'])
            self.fs.write(f"view.{codelang_css}", data['css'])

            # update cache
            fs = self.fs
            wiz = self.manager.wiz
            dicdata = fs.read.json("dic.json")

            wiz.server.socket.bind()
            return self

        def delete(self):
            self.fs.delete()
