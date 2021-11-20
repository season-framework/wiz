import season
import datetime
import json
import os

class Controller:
    def __startup__(self, framework):
        self.__framework__ = framework
        self._css = []
        self._js = []
        self._exportjs = {}

        self.__framework__.response.data.set(css=self._css)
        self.__framework__.response.data.set(js=self._js)
        self.__framework__.response.data.set(exportjs=self._exportjs)

        framework.session = framework.lib.session.to_dict()

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
