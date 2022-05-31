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

class Theme:
    def __init__(self, wiz):
        self.wiz = wiz
        self.branch = wiz.branch

    def basepath(self):
        branch = self.branch()
        return os.path.join(season.path.project, "branch", branch, "themes")

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
                code = wiz.response.template(code, **kwargs)

                return markupsafe.Markup(code)