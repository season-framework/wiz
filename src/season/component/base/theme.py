import season
import os
import markupsafe
from abc import *

class Theme(metaclass=ABCMeta):
    def __init__(self, wiz):
        self.wiz = wiz
        self.branch = wiz.branch

    @abstractmethod
    def basepath(self):
        pass

    def list(self):
        fs = season.util.os.FileSystem(self.basepath())
        themes = fs.files()
        res = []
        for filename in themes:
            layouts = fs.files(os.path.join(filename, 'layout'))
            for layout in layouts:
                res.append(filename + "/" + layout)
        return res

    def __call__(self, id):
        if id is None: return None
        return self.Package(self, id)

    class Package:
        def __init__(self, manager, theme):
            self.manager = manager
            self.theme = theme
            self.fs = season.util.os.FileSystem(os.path.join(manager.basepath(), theme))

        def layout(self, layout):
            return self.Layout(self, layout)

        class Layout:
            def __init__(self, package, layout):
                theme = package.theme
                manager = package.manager
                self.wiz = manager.wiz
                self.layout = layout
                self.fs = season.util.os.FileSystem(os.path.join(manager.basepath(), theme, "layout", layout))

            def view(self, viewpath, view=None):
                wiz = self.wiz
                _, ext = os.path.splitext(viewpath)
                if ext[0] == ".": ext = ext[1:]
                ext = ext.lower()
                
                code = self.fs.read(viewpath)

                kwargs = wiz.response.data.get()
                kwargs['wiz'] = wiz
                if view is not None:
                    kwargs['view'] = markupsafe.Markup(view)

                code = wiz.compiler(ext).compile(code)
                code = wiz.response.template(code, filename=self.fs.abspath(viewpath), **kwargs)

                return markupsafe.Markup(code)