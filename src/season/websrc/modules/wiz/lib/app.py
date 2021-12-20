import abc
import datetime
import git
import os

class Base(metaclass=abc.ABCMeta):
    def __init__(self, wiz):
        framework = self.framework = wiz.framework
        self.branch = wiz.branch
        branchpath = self.branchpath()

        # create master branch if not exists
        fs = framework.model("wizfs", module="wiz").use(branchpath)
        if fs.isdir(".") == False:
            fs.makedirs(fs.abspath("."))

    """ Abstract Methods
    """
    @abc.abstractmethod
    def __branchpath__(self):
        pass

    @abc.abstractmethod
    def __load__(self, data, fs):
        pass

    @abc.abstractmethod
    def __update__(self, data, fs):
        pass
    
    """ API Methods
    """
    def branchpath(self):
        branch = self.branch()
        target = self.__branchpath__()
        return f"wiz/branch/{branch}/{target}"

    def cache(self):
        branch = self.branch()
        target = self.__branchpath__()
        fs = self.framework.model("wizfs", module="wiz").use(f"wiz/cache/{branch}/branch/{target}")
        return fs

    def clean(self):
        fs = self.framework.model("wizfs", module="wiz").use(self.branchpath())
        cachefs = self.cache()
        cachefs.delete()

        apps = self.rows()

        for app in apps:
            app_id = app['package']['id']
            namespace = app['package']['namespace']
            apppath = fs.abspath(app_id)
            cachefs.copy(apppath, namespace)
            cachefs.write(f"{namespace}/{app_id}", timestamp)

        return self

    def load(self, path, code=True):
        branch = self.branch()
        fs = self.framework.model("wizfs", module="wiz").use(os.path.join(self.branchpath(), path))

        # load app package data
        app = dict()
        app["package"] = fs.read_json(f"app.json")
        try: app["dic"] = fs.read_json(f"dic.json")
        except: app["dic"] = {}

        # if require code data
        if code:
            return self.__load__(app, fs)

        return app

    def update(self, data):
        branch = self.branch()
        
        # check required attributes
        required = ['package', 'dic']
        for key in required:
            if key not in data: 
                raise Exception(f"wiz app: '`{key}`' not defined")

        required = ['id', 'namespace']
        for key in required:
            if key not in data['package']: 
                raise Exception(f"wiz app: '`package.{key}`' not defined")

        # set timestamp
        package = data['package']
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 'created' not in package:
            package['created'] = timestamp
        package['updated'] = timestamp
        data['package'] = package

        app_id = package['id']
        namespace = package['namespace']

        allowed = "qwertyuiopasdfghjklzxcvbnm.-_1234567890"
        for ns in namespace:
            if ns not in allowed:
                raise Exception(f"wiz app: only alphabet and number and -, _ in namespace")
        

        prevdata = self.get(app_id)
        if prevdata is not None:
            prev_namespace = prevdata['package']['namespace']
        else:
            prev_namespace = namespace
        
        if len(namespace) < 4:
            raise Exception(f"wiz app: namespace length at least 4")

        cachefs = self.cache()
        fs = self.framework.model("wizfs", module="wiz").use(os.path.join(self.branchpath(), app_id))

        update_enabled = False

        # if cache already exist, check app_id match
        if cachefs.isdir(namespace):
            nschecker = f"{namespace}/{app_id}"
            if cachefs.isfile(nschecker):
                cachefs.delete(namespace)
                update_enabled = True
        else:
            update_enabled = True
            
        if update_enabled == False:
            raise Exception(f"wiz app: namespace already exists")

        # if namespace changed, delete before
        if prev_namespace != namespace:
            cachefs.delete(prev_namespace)

        fs.write_json("app.json", data['package'])
        fs.write_json("dic.json", data['dic'])

        self.__update__(data, fs)

        # copy to cache
        apppath = fs.abspath()
        cachefs.copy(apppath, namespace)
        cachefs.write(f"{namespace}/{app_id}", timestamp)

        return self
    
    def delete(self, app_id):
        branch = self.branch()

        data = self.get(app_id)
        if data is None:
            return self

        app_id = data['package']['id']
        namespace = data['package']['namespace']
        if len(app_id) == 0 or len(namespace) == 0:
            return self

        cachefs = self.cache()
        fs = self.framework.model("wizfs", module="wiz").use(self.branchpath())
        fs.delete(app_id)
        cachefs.delete(namespace)

        return self

    def get(self, app_id):
        try:
            fs = self.framework.model("wizfs", module="wiz").use(self.branchpath())
            
            # if app_id exists in route
            if fs.isfile(f"{app_id}/app.json"):
                return self.load(app_id)
            
            # if not exists, find by namespace
            cachefs = self.cache()
            if cachefs.isfile(f"{app_id}/app.json"):
                app = cachefs.read_json(f"{app_id}/app.json")
                app_id = app["id"]
                if fs.isfile(f"{app_id}/app.json"):
                    return self.load(app_id)

            # if not exists in cache, find all data
            apps = self.rows()
            for app in apps:
                if app['package']['namespace'] == app_id:
                    app_id = app['package']['id']
                    namespace = app['package']['namespace']

                    # copy to cache
                    apppath = fs.abspath(app_id)
                    cachefs.copy(apppath, namespace)
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cachefs.write(f"{namespace}/{app_id}", timestamp)
                    return self.load(app_id)

        except:
            pass
        return None
    
    def rows(self, full=False):
        fs = self.framework.model("wizfs", module="wiz").use(self.branchpath())
        routes = fs.files()
        res = []
        for app_id in routes:
            if fs.isfile(f"{app_id}/app.json"):
                res.append(self.load(app_id, full))

        res.sort(key=lambda x: x['package']['namespace'])
        return res

    def dic(self, app_id):
        fs = self.framework.model("wizfs", module="wiz").use(self.branchpath())
        return fs.read_json(f"{app_id}/dic.json")


class App(Base):
    
    def __init__(self, wiz):
        super().__init__(wiz)

    def __branchpath__(self):
        return "apps"

    def __load__(self, data, fs):
        def readfile(key, filename, default=""):
            try:
                data[key] = fs.read(filename)
            except:
                data[key] = default
            return data

        data = readfile("controller", "controller.py")
        data = readfile("api", "api.py")
        data = readfile("socketio", "socketio.py")
        data = readfile("html", "html.dat")
        data = readfile("js", "js.dat")
        data = readfile("css", "css.dat")

        return data    

    def __update__(self, data, fs):
        # check required data
        required = ['controller', 'api', 'socketio', 'html', 'js', 'css']
        for key in required:
            if key not in data: 
                raise Exception(f"wiz app: '`{key}`' not defined")

        # save data
        fs.write("controller.py", data['controller'])
        fs.write("api.py", data['api'])
        fs.write("socketio.py", data['socketio'])
        fs.write("html.dat", data['html'])
        fs.write("js.dat", data['js'])
        fs.write("css.dat", data['css'])
        

class Route(Base):
    
    def __init__(self, wiz):
        super().__init__(wiz)

    def __branchpath__(self):
        return "routes"

    def __load__(self, data, fs):
        def readfile(key, filename, default=""):
            try:
                data[key] = fs.read(filename)
            except:
                data[key] = default
            return data

        data = readfile("controller", "controller.py")
        return data    

    def __update__(self, data, fs):
        # check required data
        required = ['controller']
        for key in required:
            if key not in data: 
                raise Exception(f"wiz app: '`{key}`' not defined")

        # save data
        fs.write("controller.py", data['controller'])
        