import season
import os

class Compiler:
    def __init__(self, wiz):
        self.wiz = wiz
        self.branch = wiz.branch

    def basepath(self):
        branch = self.branch()
        return os.path.join(season.path.project, 'plugin', 'compiler')

    def list(self):
        fs = season.util.os.FileSystem(self.basepath())
        compilers = fs.files()
        res = []
        for filename in compilers:
            res.append(os.path.splitext(filename)[0])
        return res

    def __call__(self, id):
        if id is None: return None
        return self.Package(self, id)

    class Package:
        def __init__(self, manager, lang):
            self.manager = manager
            self.fs = season.util.os.FileSystem(manager.basepath())
            self.lang = lang

        def compile(self, code, **kwargs):
            wiz = self.manager.wiz
            fs = self.fs
            lang = self.lang
            if code is None: return ""
            if len(code) == 0: return ""
            if fs.isfile(lang + ".py") == False: return code
            logger = wiz.logger(f"[plugin/compiler/{lang}]")
            compiler = fs.read(lang + ".py")
            compiler = season.util.os.compiler(compiler, name=fs.abspath(lang + ".py"), logger=logger, wiz=wiz)
            return compiler['compile'](wiz, code, kwargs)