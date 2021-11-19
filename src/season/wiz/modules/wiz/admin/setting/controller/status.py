import season
import sys
import requests
import json

class Controller(season.interfaces.wiz.ctrl.admin.setting.view):

    def __startup__(self, framework):
        super().__startup__(framework)
        
    def __default__(self, framework):
        self.js('js/status.js')

        isupdate = False
        latest_version = "Unknown"

        try:
            packageinfo = json.loads(requests.get("https://raw.githubusercontent.com/season-framework/season-flask-wiz/main/wiz-package.json").text)
            latest_version = packageinfo['version']
            versioninfo = packageinfo['version'].split(".")
            wizversion = self.db.package.version.split(".")
            if int(wizversion[0]) < int(versioninfo[0]):
                isupdate = True
            if int(wizversion[0]) == int(versioninfo[0]):
                if int(wizversion[1]) < int(versioninfo[1]):
                    isupdate = True
                if int(wizversion[1]) == int(versioninfo[1]):
                    if int(wizversion[2]) < int(versioninfo[2]):
                        isupdate = True
        except:
            pass

        kwargs = dict()
        try: kwargs["SEASON_VERSION"] = season.version
        except: kwargs["SEASON_VERSION"] = "<= 0.3.8"
        kwargs["PYTHON_VERSION"] = sys.version
        kwargs["latest_version"] = latest_version
        kwargs["isupdate"] = isupdate
        kwargs["is_dev"] =self.wiz.is_dev()
        framework.response.render('status.pug', **kwargs)

    # def wizsetting(self, framework):
    #     self.js('general/wizsetting.js')
    #     self.exportjs(themes=self.wiz.themes())
    #     framework.response.render('general/wizsetting.pug', is_dev=self.wiz.is_dev())
