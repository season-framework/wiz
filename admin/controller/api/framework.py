import season
import os
import shutil
import json

class Controller(season.interfaces.wiz.admin.api):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.fs = framework.model("wizfs", module="wiz")

    def upload(self, framework):
        files = framework.request.files()
        path = framework.request.query("path", True)
        name = framework.request.query("name", True)
        fs = self.fs.use(path + "/" + name)
        for file in files:
            try:
                if len(file.filename) == 0: continue
                filename = file.filename
                fs.write(filename, file)
            except Exception as e:
                pass

        return self.status(200, True)

    def delete(self, framework):
        path = framework.request.query("path", True)
        name = framework.request.query("name", True)
        fs = self.fs.use(path)
        fs.delete(name)
        self.status(200, True)

    def delete_bulk(self, framework):
        data = framework.request.query("data", True)
        data = json.loads(data)

        for item in data:
            path = item['path']
            name = item['name']
            fs = self.fs.use(path)
            fs.delete(name)
        self.status(200, True)

    def rename(self, framework):
        path = framework.request.query("path", True)
        name = framework.request.query("name", True)
        rename = framework.request.query("rename", True)
        ftype = framework.request.query("type", "folder")

        fs = self.fs.use(path)
        if len(name) > 0:
            if os.path.isfile(fs.abspath(name)) or os.path.isdir(fs.abspath(name)):
                shutil.move(fs.abspath(name), fs.abspath(rename))
                self.status(200, True)
        
        if len(rename) > 0:
            newtarget = fs.abspath(rename)
            if os.path.isfile(newtarget) or os.path.isdir(newtarget):
                self.status(401, "Already Exists")

            if ftype == 'file':
                ext = os.path.splitext(rename)[1]
                extmap = {}
                extmap[".py"] = "python"
                extmap[".js"] = "javascript"
                extmap[".ts"] = "typescript"
                extmap[".css"] = "css"
                extmap[".less"] = "less"
                extmap[".sass"] = "scss"
                extmap[".scss"] = "scss"
                extmap[".html"] = "html"
                extmap[".pug"] = "pug"
                if ext in extmap:
                    fs.write(rename, "")
                else:
                    self.status(402, "Not Supported File Name")
            else:
                os.makedirs(newtarget)
            self.status(200, True)

        self.status(404, "Error")

    def update(self, framework):
        path = framework.request.query("path", True)
        name = framework.request.query("name", True)
        text = framework.request.query("text", True)
        
        fs = self.fs.use(path)
        fs.write(name, text)

        self.status(200, True)

    def tree(self, framework):
        path = framework.request.query("path", True)
        name = framework.request.query("name", True)
        _type = framework.request.query("type", "folder")
        if path.startswith("/"):
            path = path[1:]

        if _type == 'file':
            ext = os.path.splitext(name)[1].lower()

            # vscode
            extmap = {}
            extmap[".py"] = "python"
            extmap[".js"] = "javascript"
            extmap[".ts"] = "typescript"
            extmap[".css"] = "css"
            extmap[".less"] = "less"
            extmap[".sass"] = "scss"
            extmap[".scss"] = "scss"
            extmap[".html"] = "html"
            extmap[".pug"] = "pug"
            extmap[".json"] = "json"
            if ext in extmap:
                fs = self.fs.use(path)
                self.status(201, {"text": fs.read(name), "path": path, "name": name, "language": extmap[ext]})
            
            # image view
            extmap = {}
            extmap[".png"] = "image"
            extmap[".jpeg"] = "image"
            extmap[".jpg"] = "image"
            extmap[".ico"] = "image"
            extmap[".icon"] = "image"
            extmap[".svg"] = "image"
            if ext in extmap:
                target = path + "/" + name
                if target.startswith("."): target = target[1:]
                self.status(202, {"path": path, "name": name, "url": target})

            self.status(404, "not support file")

        namespace = os.path.join(path, name)
        fs = self.fs.use(namespace)
        if os.path.isfile(fs.abspath(".")) == False and os.path.isdir(fs.abspath(".")) == False:
            self.status(404, [])

        files = fs.list()

        rows = []
        for file in files:
            obj = dict()
            obj["path"] = namespace
            obj["name"] = file
            obj["sub"] = []
            obj["type"] = "folder"
            if os.path.isfile(fs.abspath(file)):
                obj["type"] = "file"
            rows.append(obj)

        self.status(200, rows)