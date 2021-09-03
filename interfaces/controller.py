import season
import datetime
import json
import os

class base:
    def __startup__(self, framework):
        self.__framework__ = framework
        self._css = []
        self._js = []
        self._exportjs = {}

        self.__framework__.response.data.set(css=self._css)
        self.__framework__.response.data.set(js=self._js)
        self.__framework__.response.data.set(exportjs=self._exportjs)
        self.__framework__.response.data.set(session=dict(framework.session))

        self.config = framework.config.load('wiz').data
        self.db = framework.model("wiz", module="wiz")
    
    def status(self, status_code=200, data=dict()):
        res = season.stdClass()
        res.code = status_code
        res.data = data
        res = json.dumps(res, default=self.json_default)
        return self.__framework__.response.send(res, content_type='application/json')

    def exportjs(self, **args):
        for key in args:
            v = args[key]
            self._exportjs[key] = json.dumps(v, default=self.json_default)
        
        self.__framework__.response.data.set(exportjs=self._exportjs)

    def css(self, url):
        framework = self.__framework__
        url = os.path.join(framework.modulename, url)
        self._css.append(url)
        self.__framework__.response.data.set(css=self._css)
    
    def js(self, url):
        framework = self.__framework__
        url = os.path.join(framework.modulename, url)
        self._js.append(url)
        self.__framework__.response.data.set(js=self._js)

    def parse_json(self, jsonstr, default=None):
        try:
            return json.loads(jsonstr)
        except:
            pass
        return default

    def json_default(self, value):
        if isinstance(value, datetime.date): 
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return str(value).replace('<', '&lt;').replace('>', '&gt;')

class api(base):
    def __startup__(self, framework):
        super().__startup__(framework)

    def __error__(self, framework, e):
        framework.response.json({"status": 500, "error": str(e)})
