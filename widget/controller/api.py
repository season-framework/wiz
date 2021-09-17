import season

class Controller(season.interfaces.wiz.controller.api):

    def __startup__(self, framework):
        super().__startup__(framework)
        if self.config.acl is not None: self.config.acl(framework)

    def info(self, framework):
        app_id = framework.request.segment.get(0, True)
        db = framework.model('wiz', module='wiz')
        info = db.get(id=app_id)
        if info is None:
            self.status(404)
        self.status(200, info)

    def search(self, framework):
        data = framework.request.query()
        data['or'] = dict()
        if 'text' in data:
            if len(data['text']) > 0:
                data['or']['title'] = data['text']
                data['or']['app_id'] = data['text']
                data['or']['category'] = data['text']
            del data['text']
        data['like'] = 'title,app_id'
        data['orderby'] = '`title` ASC'
        rows = self.db.search(**data)
        return self.status(200, rows)

    def update(self, framework):
        _info = framework.request.query()
        if 'id' not in _info or _info['id'] == 'new':
            self.status(400, "Bad Request")
        info = self.db.get(id=_info['id'])
        stat, _ = self.db.upsert(_info)
        
        self.db.set_update_view(True)
        self.db.render(info['id'])
        self.db.routes()

        if stat: self.status(200, info['id'])
        self.status(500, info['id'])

    def delete(self, framework):
        app_id = framework.request.query('app_id', True)
        self.db.delete(id=app_id)
        return self.status(200, True)