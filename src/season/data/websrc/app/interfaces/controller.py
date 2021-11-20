import os
import season
import json
import datetime

class base:    
    def __init__(self, framework):
        self.__framework__ = framework
        
    def status(self, status_code=200, data=dict()):
        res = season.stdClass()
        res.code = status_code
        res.data = data
        res = json.dumps(res, default=self.json_default)
        return self.__framework__.response.send(res, content_type='application/json')

    def json_default(self, value):
        if isinstance(value, datetime.date): 
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return str(value).replace('<', '&lt;').replace('>', '&gt;')

    def redirect(self, url):
        baseurl = '/' + self.__framework__.modulename
        return self.__framework__.response.redirect(os.path.join(baseurl, url))