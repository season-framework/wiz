import season
import datetime

class Controller(season.interfaces.wiz.admin.api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def build(self, framework):
        self.wiz.flush()
        self.wiz.build()
        self.status(200, True)

    def commit_log(self, framework):
        app_id = framework.request.query("id", True)
        rows = self.wiz.rows(id=app_id, orderby="`version` DESC", fields="id,version,version_message,user_id,version_name")
        self.status(200, rows)

    def commit(self, framework):
        info = framework.request.query()
        if 'id' not in info or info['id'] == 'new':
            self.status(400, "Bad Request")
        info['version'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        if 'updated' in info:
            del info['updated']
        stat, _ = self.db.upsert(info)
        if stat: self.status(200, info['id'])
        self.status(500, info['id'])

    def commit_get(self, framework):
        app_id = framework.request.query("id", True)
        version = framework.request.query("version", True)
        db = self.wiz
        info = db.get(id=app_id, version=version)
        if info is None:
            self.status(404)
        self.status(200, info)

    def info(self, framework):
        app_id = framework.request.segment.get(0, True)
        db = self.wiz
        info = db.get(id=app_id, version="master")
        if info is None:
            self.status(404)
        self.status(200, info)

    def tree(self, framework):
        category = ['widget', 'page']
        try:
            category = self.config.category
        except:
            pass
        db = self.wiz
        for i in range(len(category)):
            c = category[i]
            if type(c) == str:
                category[i] = {"id": category[i], "title": category[i]}
            category[i]['data'] = db.select(fields="id,title,namespace", version="master", category=category[i]['id'], orderby="title ASC")
        self.status(200, category)

    def search(self, framework):
        data = framework.request.query()
        data['version'] = 'master'
        data['or'] = dict()
        if 'text' in data:
            if len(data['text']) > 0:
                data['or']['title'] = data['text']
                data['or']['namespace'] = data['text']
                data['or']['app_id'] = data['text']
                data['or']['category'] = data['text']
                data['or']['html'] = data['text']
                data['or']['js'] = data['text']
                data['or']['css'] = data['text']
                data['or']['api'] = data['text']
                data['or']['kwargs'] = data['text']
                
            del data['text']
        data['like'] = 'title,app_id,html,js,css,api,kwargs,namespace'
        data['orderby'] = '`title` ASC'
        rows = self.db.search(**data)
        return self.status(200, rows)

    def update(self, framework):
        _info = framework.request.query()
        if 'id' not in _info or _info['id'] == 'new':
            self.status(400, "Bad Request")

        info = self.db.get(id=_info['id'], version="master")
        _info['version'] = "master"
        stat, _ = self.db.upsert(_info)
        try:
            if info['socketio'] != _info['socketio']:
                fs = framework.model("wizfs", module="wiz")
                fs.write(".timestamp", datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        except:
            pass

        try:
            if info['html'] != _info['html'] or info['js'] != _info['js'] or info['css'] != _info['css'] or info['kwargs'] != _info['kwargs'] or info['socketio'] != _info['socketio']:
                config = framework.config.load("wiz")
                if config.devtools:
                    namespace = "/wiz/devtools/reload/" + info["id"]
                    if info['socketio'] != _info['socketio']:
                        framework.socketio.emit("reload", True, namespace=namespace, broadcast=True)
                    else:
                        framework.socketio.emit("reload", False, namespace=namespace, broadcast=True)
        except:
            pass

        if stat: self.status(200, info['id'])
        self.status(500, info['id'])

    def delete(self, framework):
        app_id = framework.request.query('app_id', True)
        self.db.delete(id=app_id)
        return self.status(200, True)