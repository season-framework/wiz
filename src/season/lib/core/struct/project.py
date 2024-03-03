import season
import os

class Project:
    def __init__(self, wiz):
        self.wiz = wiz
        self._project = None

        if wiz.server.config.boot.bundle:
            self._project = "main"
            return

        if wiz.request is not None:
            try:
                project = wiz.request.cookies("season-wiz-project", "main")
            except:
                project = "main"
            if self.exists(project):
                self._project = project
    
        if self._project is None:
            self._project = "main"

    def exists(self, project):
        wiz = self.wiz
        server = wiz.server
        projectbasepath = server.path.project
        projectpath = os.path.join(projectbasepath, project)
        if os.path.isdir(projectpath):
            return True
        return False

    def list(self):
        server = self.wiz.server
        fs = season.util.filesystem(server.path.project)
        return fs.list()

    def path(self, *args):
        wiz = self.wiz
        server = wiz.server
        projectbasepath = server.path.project
        projectpath = os.path.join(projectbasepath, self._project, *args)
        return projectpath

    def checkout(self, project):
        wiz = self.wiz
        if self.exists(project):
            if wiz.response is not None:
                param = dict()
                param["season-wiz-project"] = project
                wiz.response.cookies.set(**param)
            self._project = project
        return self._project

    def fs(self, *args):
        return season.util.filesystem(self.path(*args))

    def dev(self, *args):
        wiz = self.wiz
        if len(args) == 0:
            try:
                try:
                    is_dev = wiz.request.cookies("season-wiz-devmode", "false")
                except:
                    is_dev = "false"
                if is_dev == "false":
                    is_dev = False
                else: 
                    is_dev = True

                if self._project not in ['main']:
                    is_dev = True
            except:
                is_dev = False
        else:
            DEVMODE = args[0]
            wiz = self.wiz
            if DEVMODE == True: 
                DEVMODE = "true"
                is_dev = True
            else: 
                DEVMODE = "false"
                is_dev = False
            param = dict()
            param["season-wiz-devmode"] = DEVMODE
            wiz.response.cookies.set(**param)
            
        return is_dev
    
    def __call__(self, project=None):
        if project is None:
            return self._project
        project = self.checkout(project)
        return project
    
    def filter(self):
        fs = self.wiz.fs("plugin")
        plugins = fs.ls()

        logger = self.wiz.logger(f"app/filter")

        for plugin in plugins:
            code = fs.read(os.path.join(plugin, "filter.py"), None)
            if code is None:
                continue
            name = fs.abspath(os.path.join(plugin, "filter.py"))
            self.wiz.ide.plugin.name = plugin
            season.util.compiler().build(code, name=name, logger=logger, wiz=self.wiz)
        
        self.wiz.ide.plugin.name = None
            