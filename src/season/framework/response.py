import json
import os

class response:
    def __init__(self, framework):
        self.framework = framework
        self._flask = framework.flask
        self.data = response._data(framework)
        self.headers = self._headers()
        self.cookies = self._cookies()
        self.status_code = None
        self.mimetype = None
        self.modulename = framework.modulename

    def lang(self, lang):
        self.language(lang)

    def language(self, lang):
        lang = lang[:2].upper()
        self.framework.__language__ = lang
        self.cookies.set('framework-language', lang)

    def set_status(self, status_code):
        self.status_code = status_code

    def set_mimetype(self, mimetype):
        self.mimetype = mimetype

    def abort(self, code=500):
        self._flask.abort(code)

    def error(self, code=404, response="ERROR"):
        event = self.framework.core.CLASS.RESPONSE.STATUS(code=code, response=response)
        raise event
        
    # response functions
    def redirect(self, url):
        if url.startswith('http') == False:
            url = os.path.abspath(os.path.join("/" + self.modulename, url))
        self.status_code = 302
        resp = self._flask.redirect(url)
        return self._build(resp)

    def download(self, filepath, as_attachment=True, filename=None):
        if os.path.isfile(filepath):
            resp = self._flask.send_file(filepath, as_attachment=as_attachment, attachment_filename=filename)
            return self._build(resp)
        self._flask.abort(404)
    
    def send(self, message, content_type=None):
        resp = self._flask.Response(str(message))
        if content_type is not None:
            self.headers.set('Content-Type', content_type)
        return self._build(resp)

    def json(self, obj):
        try:
            obj = dict(obj)
        except:
            pass
        obj = json.dumps(obj, default=self.framework.core.json_default, ensure_ascii=False)
        resp = self._flask.Response(str(obj))
        self.headers.set('Content-Type', 'application/json')
        return self._build(resp)

    def status(self, *args, **kwargs):
        data = dict()
        if len(args) == 0:
            status_code = 200
        elif len(args) == 1:
            status_code = args[0]
            for key in kwargs:
                data[key] = kwargs[key]
        elif len(args) > 1:
            status_code = args[0]
            data = args[1]

        res = dict()
        res['code'] = status_code
        if data is not None:
            res['data'] = data
        res = json.dumps(res, default=self.framework.core.json_default, ensure_ascii=False)
        return self.send(res, content_type='application/json')

    def template_from_string(self, template_string, **kwargs):
        self.data.set(**kwargs)
        data = self.data.get()
        html = self._flask.render_template_string(template_string, **data)
        return html

    def template(self, template_uri, module=None, **args):
        if module is None: module = self.modulename
        TEMPLATE_PATH = os.path.join(self.framework.core.PATH.TEMPLATE, module, template_uri)
        TEMPLATE_URI = os.path.join(module, template_uri)
        self.data.set(**args)
        if os.path.isfile(TEMPLATE_PATH):
            data = self.data.get()
            resp = self._flask.render_template(TEMPLATE_URI, **data)
            return resp
        return None

    def render(self, template_uri, module=None, **args):
        resp = self.template(template_uri, module=module, **args)
        if resp is not None:
            return self.send(resp, "text/html")
        self._flask.abort(404)

    # template varialbes
    class _data:
        def __init__(self, framework):
            self.framework = framework
            self.data = dict()
        
        def get(self, key=None):
            if key is None:
                return self.data
            if key in self.data:
                return self.data[key]
            return None

        def set(self, **args):
            for key, value in args.items():
                self.data[key] = value

        def set_json(self, **args):
            for key, value in args.items():
                self.data[key] = json.dumps(value, default=self.framework.core.json_default, ensure_ascii=False)

    # internal classes
    class _headers:
        def __init__(self):
            self.headers = {}
        
        def get(self):
            return self.headers

        def set(self, key, value):
            self.headers[key] = value

        def load(self, headers):
            self.headers = headers

        def flush(self):
            self.headers = {}

    class _cookies:
        def __init__(self):
            self.cookies = {}
        
        def get(self):
            return self.cookies

        def set(self, key, value):
            self.cookies[key] = value

        def load(self, cookies):
            self.cookies = cookies

        def flush(self):
            self.cookies = {}

    # build response function
    def _build(self, response):
        headers = self.headers.get()
        for key in headers:
            response.headers[key] = headers[key]

        cookies = self.cookies.get()
        for key in cookies:
            response.set_cookie(key, cookies[key])
        
        if self.status_code is not None:
            response.status_code = self.status_code
        else:
            response.status_code = 200

        if self.mimetype is not None:
            response.mimetype = self.mimetype

        event = self.framework.core.CLASS.RESPONSE.STATUS(code=response.status_code, response=response)
        raise event
