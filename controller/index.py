import season
import json
import datetime
import urllib

class Controller(season.interfaces.wiz.controller.api):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.framework = framework

    def json_default(self, value):
        if isinstance(value, datetime.date): 
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return ""

    def status(self, status_code=200, data=None):
        res = season.stdClass()
        res.code = status_code
        res.data = data
        res = json.dumps(res, default=self.json_default)
        return self.__framework__.response.send(res, content_type='application/json')

    def __error__(self, framework, err):
        self.status(500, str(err))

    def __default__(self, framework):
        framework.response.redirect("widget")

    def api(self, framework):
        framework.response.status = self.status
        app_id = framework.request.segment.get(0, True)
        fnname = framework.request.segment.get(1, True)
        wiz = self.db.get(id=app_id, fields="api")
        if wiz is None: self.status(404)
        view_api = wiz['api']
        if view_api is None: self.status(404)
        fn = {'__file__': 'season.Spawner', '__name__': 'season.Spawner', 'framework': framework}
        exec(compile(view_api, 'season.Spawner', 'exec'), fn)
        if '__startup__' in fn: fn['__startup__'](framework)
        fn[fnname](framework)

    def export(self, framework):
        if self.config.acl is not None: self.config.acl(framework)
        app_id = framework.request.segment.get(0, True)
        info = self.db.get(id=app_id)
        if info is None:
            framework.response.abort(404)

        app_title = info['title']
        app_title = urllib.parse.quote(app_title)
        
        framework.response.headers.load({'Content-Disposition': f'attachment;filename={app_title}.json'})
        framework.response.set_mimetype('application/json')
        framework.response.send(json.dumps(info, default=self.json_default))