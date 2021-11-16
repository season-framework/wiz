import season
import os
import shutil
import json

SAMPLE = season.stdClass()
SAMPLE.HEADER = """title SEASON WIZ

meta(charset='utf-8')
meta(name='viewport' content='width=device-width, initial-scale=1, viewport-fit=cover')
meta(http-equiv='X-UA-Compatible' content='ie=edge')
meta(name='msapplication-TileColor' content='#206bc4')
meta(name='theme-color' content='#206bc4')
meta(name='apple-mobile-web-app-status-bar-style' content='black-translucent')
meta(name='apple-mobile-web-app-capable' content='yes')
meta(name='mobile-web-app-capable' content='yes')
meta(name='HandheldFriendly' content='True')
meta(name='MobileOptimized' content='320')

link(href='/resources/themes/<THEME_NAME>/libs/fontawesome/css/all.min.css' rel='stylesheet')
script(src='/resources/themes/<THEME_NAME>/libs/jquery/jquery-3.5.1.min.js')
"""

SAMPLE.LAYOUT = """doctype 5

html(ng-app="app")
    head
        {$ wiz.theme('<THEME_NAME>', '<LAYOUT_NAME>', '<LAYOUT_FILE>') $}
        {$ wiz.theme('default', 'season', 'header.pug') $}
        
    body.antialiased
        script(src='/resources/themes/<themename>/libs/jquery.js')

        .page
            .preview
                {$ view $}

            style.
                html,
                body {
                    overflow: auto;
                }

                body {
                    padding: 32px;
                }

                .page {
                    background: transparent;
                }
"""

class Controller(season.interfaces.wiz.ctrl.admin.workspace.api):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.fs = framework.model("wizfs", module="wiz")
        BASEPATH = self.wiz.branchpath()
        BASEPATH = os.path.join(BASEPATH, "themes")
        self.BASEPATH = BASEPATH
        self.SEGMENT_BASE = len(self.BASEPATH.split("/"))
        self.supportfiles = framework.config.load("wiz").get("supportfiles", {})

    def upload(self, framework):
        files = framework.request.files()
        path = framework.request.query("path", True)
        name = framework.request.query("name", True)
        filepath = framework.request.query("filepath", True)
        filepath = json.loads(filepath)

        if len(filepath) != len(files):
            return framework.response.status(400, True)

        fs = self.fs.use(path + "/" + name)
        for i in range(len(files)):
            try:
                file = files[i]
                if len(file.filename) == 0: continue
                filename = filepath[i]
                fs.write_file(filename, file)
            except Exception as e:
                pass

        return framework.response.status(200, True)

    def delete(self, framework):
        path = framework.request.query("path", True)
        name = framework.request.query("name", True)
        fs = self.fs.use(path)
        fs.delete(name)
        framework.response.status(200, True)

    def delete_bulk(self, framework):
        data = framework.request.query("data", True)
        data = json.loads(data)

        for item in data:
            path = item['path']
            name = item['name']
            fs = self.fs.use(path)
            fs.delete(name)
        framework.response.status(200, True)

    def rename(self, framework):
        path = framework.request.query("path", True)
        name = framework.request.query("name", True)
        rename = framework.request.query("rename", True)
        ftype = framework.request.query("type", "folder")
        segment = path.split("/")

        fs = self.fs.use(path)
        if len(name) > 0:
            if os.path.isfile(fs.abspath(name)) or os.path.isdir(fs.abspath(name)):
                shutil.move(fs.abspath(name), fs.abspath(rename))
                framework.response.status(200, True)
        
        if len(rename) > 0:
            newtarget = fs.abspath(rename)
            if os.path.isfile(newtarget) or os.path.isdir(newtarget):
                framework.response.status(401, "Already Exists")

            if ftype == 'file':
                ext = os.path.splitext(rename)[1]
                extmap = self.supportfiles
                if ext in extmap:
                    fs.write(rename, "")
                else:
                    framework.response.status(402, "Not Supported File Name")
            else:
                os.makedirs(newtarget)
                if len(segment) == self.SEGMENT_BASE + 2 and segment[-1] == 'layout':
                    fs = self.fs.use(os.path.join(path, rename))
                    if fs.isfile("header.pug") == False: fs.write("header.pug", SAMPLE.HEADER)
                    if fs.isfile("layout.pug") == False: fs.write("layout.pug", SAMPLE.LAYOUT)      

            framework.response.status(200, True)

        framework.response.status(404, "Error")

    def update(self, framework):
        path = framework.request.query("path", True)
        name = framework.request.query("name", True)
        text = framework.request.query("text", True)
        
        fs = self.fs.use(path)
        fs.write(name, text)

        framework.response.status(200, True)

    def tree(self, framework):
        path = framework.request.query("path", True)
        name = framework.request.query("name", True)
        namespace = os.path.join(path, name)
        segment = path.split("/")

        def objbuilder(_path, _name, _type, _sub=[]):
            obj = dict()
            obj["path"] = _path
            obj["name"] = _name
            obj["sub"] = _sub
            obj["type"] = _type
            return obj

        if len(segment) == self.SEGMENT_BASE:
            rows = []
            rows.append(objbuilder(namespace, "layout", "layout"))
            rows.append(objbuilder(namespace, "resources", "folder"))
            framework.response.status(200, rows)

        if len(segment) == self.SEGMENT_BASE + 1:
            fs = self.fs.use(path)
            componentpath = fs.abspath(name)
            try:
                os.makedirs(componentpath)
            except:
                pass  
             
        if path.split("/")[0] == "_system":
            framework.response.status(300, {"path": path, "name": name})

        _type = framework.request.query("type", "folder")
        if path.startswith("/"):
            path = path[1:]

        if _type == 'file':
            ext = os.path.splitext(name)[1].lower()

            # vscode
            extmap = self.supportfiles
            if ext in extmap:
                fs = self.fs.use(path)
                framework.response.status(201, {"text": fs.read(name), "path": path, "name": name, "language": extmap[ext]})
            
            # image view
            extmap = {}
            extmap[".png"] = "image"
            extmap[".jpeg"] = "image"
            extmap[".jpg"] = "image"
            extmap[".ico"] = "image"
            extmap[".icon"] = "image"
            if ext in extmap:
                target = path + "/" + name
                if target.startswith("."): target = target[1:]
                framework.response.status(202, {"path": path, "name": name, "url": target})

            framework.response.status(404, "not support file")

        fs = self.fs.use(namespace)
        if os.path.isfile(fs.abspath(".")) == False and os.path.isdir(fs.abspath(".")) == False:
            framework.response.status(404, [])
        files = fs.list()
        rows = []
        for file in files:
            _type = "folder"
            if os.path.isfile(fs.abspath(file)):
                _type = "file"
            rows.append(objbuilder(namespace, file, _type))

        framework.response.status(200, rows)