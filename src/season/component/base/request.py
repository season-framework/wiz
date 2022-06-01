import re
from abc import *

class Request(metaclass=ABCMeta):
    def __init__(self, wiz):
        self.wiz = wiz
        self._flask = wiz.server.flask

    @abstractmethod
    def uri(self):
        pass

    def method(self):
        return self._flask.request.method

    def ip(self):
        return self.client_ip()

    def client_ip(self):
        return self._flask.request.environ.get('HTTP_X_REAL_IP', self._flask.request.remote_addr)

    def lang(self):
        return self.language()

    def language(self):
        try:
            lang = "DEFAULT"
            cookies = dict(self._flask.request.cookies)
            headers = dict(self._flask.request.headers)
            if 'framework-language' in cookies:
                lang = cookies['framework-language']
            elif 'Accept-Language' in headers:
                lang = headers['Accept-Language']
                lang = lang[:2]
            return lang.upper()
        except:
            return "DEFAULT"

    def match(self, pattern):
        uri = self.uri()
        x = re.search(pattern, uri)
        if x: return True
        return False

    def query(self, key=None, default=None):
        request = self.request()
        formdata = dict(request.values)

        if key is None:
            return formdata

        if key in formdata:
            return formdata[key]
        
        if default is True:
            self._flask.abort(400)
            
        return default

    def headers(self, key, default=None):
        headers = dict(self._flask.request.headers)
        if key in headers:
            return headers[key]
        return default

    def cookies(self, key, default=None):
        cookies = dict(self._flask.request.cookies)
        if key in cookies:
            return cookies[key]
        return default

    def file(self, namespace='file'):
        try:
            return self._flask.request.files[namespace]
        except:
            return None

    def files(self, namespace='file'):
        try:
            return self._flask.request.files.getlist(f'{namespace}[]')
        except:
            return []

    def request(self):
        return self._flask.request
