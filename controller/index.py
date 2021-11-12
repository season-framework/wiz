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

    # TODO: change process code
    def api(self, framework):
        app_id = framework.request.segment.get(0, True)
        fnname = framework.request.segment.get(1, True)
        wiz = self.db.get(id=app_id, fields="api,namespace")
        if wiz is None: self.status(404)
        view_api = wiz['api']
        if view_api is None: self.status(404)

        _prelogger = framework.log
        def _logger(*args):
            _prelogger(f"[{wiz['namespace']}]", *args)
        framework.log = _logger

        fn = {'__file__': 'season.Spawner', '__name__': 'season.Spawner', 'framework': framework, 'print': _logger}
        exec(compile(view_api, 'season.Spawner', 'exec'), fn)
        if '__startup__' in fn: fn['__startup__'](framework)
        fn[fnname](framework)

    # TODO: change process code
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