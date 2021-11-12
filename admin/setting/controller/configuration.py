import season
import sys
import requests
import json

class Controller(season.interfaces.wiz.ctrl.admin.setting.view):

    def __startup__(self, framework):
        super().__startup__(framework)
        
    def __default__(self, framework):
        self.js('js/configuration.js')
        self.exportjs(themes=self.wiz.themes())
        framework.response.render('configuration.pug', is_dev=self.wiz.is_dev())
