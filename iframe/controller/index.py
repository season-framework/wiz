import season
import json
import datetime

class Controller(season.interfaces.controller.api):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.framework = framework

    def json_default(self, value):
        if isinstance(value, datetime.date): 
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return ""

    def status(self, status_code=200, data=dict(), log=None):
        res = season.stdClass()
        res.code = status_code
        res.data = data
        res.log = log
        res = json.dumps(res, default=self.json_default)
        return self.__framework__.response.send(res, content_type='application/json')

    def __error__(self, framework, err):
        self.status(500)

    def __default__(self, framework):
        app_id = framework.request.segment.get(0, True)
        db = framework.model("wiz", module="wiz")
        view = db.view(app_id)
        framework.response.render('iframe.pug', view=view, app_id=app_id)
