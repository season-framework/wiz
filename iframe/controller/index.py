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
        config = self.config
        app_id = framework.request.segment.get(0, True)
        db = framework.model("wiz", module="wiz")
        db.set_update_view(True)
        view = db.render(app_id)

        if 'default' not in config.theme:
            config.theme.default = season.stdClass()
            config.theme.default.module = "wiz/theme"
            config.theme.default.view = "layout-wiz.pug"

        theme = db.get(id=app_id, fields="theme")["theme"]
        if theme not in config.theme:
            for key in config.theme:
                theme = key
                break
        theme = config.theme[theme]
        framework.response.render(theme.view, module=theme.module, view=view, app_id=app_id)