import sys
import season

class Controller(season.interfaces.wiz.ctrl.admin.setting.view):

    def __startup__(self, framework):
        super().__startup__(framework)
        kwargs = dict()
        try: kwargs["SEASON_VERSION"] = season.version
        except: kwargs["SEASON_VERSION"] = "<= 0.3.8"
        kwargs["PYTHON_VERSION"] = sys.version
        kwargs["themes"] = self.wiz.themes()

        framework.response.data.set(**kwargs)
        self.exportjs(**kwargs)
        self.js('js/configuration.js')
        
    def __error__(self, framework, err):
        framework.response.redirect('status')

    def __default__(self, framework):
        page = framework.request.segment.get(0, True)
        framework.response.render(f'{page}.pug')
