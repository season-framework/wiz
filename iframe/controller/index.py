import season
import json
import datetime

class Controller(season.interfaces.wiz.controller.base):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.framework = framework
        if self.config.acl is not None: self.config.acl(framework)

    def json_default(self, value):
        if isinstance(value, datetime.date): 
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return ""

    def status(self, status_code=200, data=dict()):
        res = season.stdClass()
        res.code = status_code
        res.data = data
        res = json.dumps(res, default=self.json_default)
        return self.__framework__.response.send(res, content_type='application/json')

    def __error__(self, framework, err):
        raise err

    def __default__(self, framework):
        app_id = framework.request.segment.get(0, True)
        db = framework.model("wiz", module="wiz")
        info = db.get(id=app_id)
        view = db.render(app_id)

        theme = info['theme']
        if theme is not None:
            theme = theme.split("/")
        else:
            theme = []

        if len(theme) != 2:
            theme = framework.config().load('wiz').get("theme_default", None)
            if theme is None:
                raise Exception("Theme Not Found")
            theme = theme.split("/")

        view = db.__theme__(theme[0], theme[1], view)
        framework.response.send(view, "text/html")