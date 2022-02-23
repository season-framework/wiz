import re

class request:
    def __init__(self, framework):
        self._flask = framework.flask
        self.framework = framework
        
    def method(self):
        return self._flask.request.method
        
    def client_ip(self):
        return self._flask.request.environ.get('HTTP_X_REAL_IP', self._flask.request.remote_addr)

    def language(self):
        try:
            if '__language__' in self.framework and self.framework.__language__ is not None:
                return self.framework.__language__
            
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

    def uri(self):
        return self.request().path

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

    def file(self):
        try:
            return self._flask.request.files['file']
        except:
            return None

    def files(self):
        try:
            return self._flask.request.files.getlist('file[]')
        except:
            return []

    def request(self):
        return self._flask.request
