from season.core.component.base.workspace import Workspace as Base, App as AppBase
from season.core.component.base.workspace import localized
from season.core.builder.ide import Build

import season
import os

class App(AppBase):
    def __init__(self, workspace):
        super().__init__(workspace)

    def __call__(self, app_id):
        if app_id is None: return self
        app_id = app_id.lower()
        app = App(self.workspace)
        app.id = app_id
        return app

    def list(self):
        fs = self.workspace.fs('app')
        apps = fs.files()
        res = []
        for app_id in apps:
            app = self(app_id).data(code=False)
            if app is None:
                continue
            res.append(app['package'])
        res.sort(key=lambda x: x['id'])
        return res

    @localized
    def fs(self, *args):
        return self.workspace.fs('app', self.id, *args)

    @localized
    def data(self, code=True):
        APP_ID = self.id
        wiz = self.wiz
        fs = self.fs()

        pkg = dict()
        pkg['package'] = fs.read.json('app.json', None)
        if pkg['package'] is None:
            return None

        pkg['package']['id'] = APP_ID
        
        viewtype = 'pug'
        if 'viewtype' in pkg['package']:
            viewtype = pkg['package']['viewtype']
        if viewtype not in ['pug', 'html']:
            viewtype = 'pug'

        def readfile(key, filename, default=""):
            try: 
                pkg[key] = fs.read(filename)
            except: 
                pkg[key] = default
            return pkg
        
        if code:
            pkg = readfile("api", "api.py")
            pkg = readfile("socketio", "socketio.py")
            pkg = readfile("view", f"view.{viewtype}")
            pkg = readfile("typescript", f"view.ts")
            pkg = readfile("scss", f"view.scss")

            pkg['dic'] = dict()
            if fs.isdir("dic"):
                dics = fs.files("dic")
                for dic in dics:
                    try:
                        lang = os.path.splitext(dic)[0]
                        lang = lang.lower()
                        pkg['dic'][lang] = fs.read(os.path.join("dic", dic), '{}')
                    except:
                        pass

        return pkg

    def before_update(self, data):
        required = ['package', 'dic', 'api', 'socketio', 'view', 'typescript', 'scss']
        for key in required:
            if key not in data: 
                raise Exception(f"'`{key}`' not defined")

        data['package']['id'] = self.id
        if len(data['package']['id']) < 3:
            raise Exception(f"id length at least 3")

        allowed = "qwertyuiopasdfghjklzxcvbnm.1234567890"
        for c in data['package']['id']:
            if c not in allowed:
                raise Exception(f"only alphabet and number and . in package id")

        return data

    def do_update(self, data):
        viewtype = 'pug'
        if 'viewtype' in data['package']:
            viewtype = data['package']['viewtype']
        if viewtype not in ['pug', 'html']:
            viewtype = 'pug'

        fs = self.fs()
        fs.write("api.py", data['api'])
        fs.write("socketio.py", data['socketio'])
        fs.write(f"view.{viewtype}", data['view'])
        fs.write("view.ts", data['typescript'])
        fs.write("view.scss", data['scss'])

class Workspace(Base):
    def __init__(self, wiz):
        super().__init__(wiz)
        self.build = Build(self)
        self.app = App(self)

    def path(self, *args):
        return os.path.join(self.wiz.server.path.ide, *args)
    
    def controller(self, namespace):
        wiz = self.wiz
        fs = self.fs("controller")
        code = fs.read(f"{namespace}.py")
        logger = wiz.logger(f"[ctrl/{namespace}]")
        ctrl = season.util.os.compiler(code, name=fs.abspath(namespace + ".py"), logger=logger, wiz=wiz)
        return ctrl['Controller']
    
    def model(self, namespace):
        wiz = self.wiz
        fs = self.fs("model")
        code = fs.read(f"{namespace}.py")
        logger = wiz.logger(f"[model/{namespace}]")
        model = season.util.os.compiler(code, name=fs.abspath(namespace + ".py"), logger=logger, wiz=wiz)
        return model['Model']
