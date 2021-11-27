import season
import json
import datetime
import urllib

class Controller(season.interfaces.wiz.ctrl.base.api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def __default__(self, framework):
        if len(self.config.data) == 0:
            framework.response.redirect("install")
        framework.response.redirect("admin")

    def api(self, framework):
        app_id = framework.request.segment.get(0, True)
        fnname = framework.request.segment.get(1, True)

        org = framework.request.segment.get
        def get(idx, default=None):
            return org(idx+2, default)
        framework.request.segment.get = get
        
        api, wiz = self.wiz.api(app_id)
        if api is None: 
            framework.response.status(404)

        if fnname not in api:
            framework.response.status(404)

        if '__startup__' in api: 
            api['__startup__'](wiz)

        api[fnname](wiz)

    def export(self, framework):
        if self.config.acl is not None: 
            self.config.acl(framework)

        mode = framework.request.segment.get(0, True)
        app_id = framework.request.segment.get(1, True)

        app = self.wiz.data.get(app_id, mode=mode)
        if app is None:
            framework.response.abort(404)

        app_title = app['package']['title']
        app_title = urllib.parse.quote(app_title)
        
        framework.response.headers.load({'Content-Disposition': f'attachment;filename={app_title}.json'})
        framework.response.set_mimetype('application/json')
        framework.response.send(json.dumps(app, default=self.json_default, ensure_ascii=False))