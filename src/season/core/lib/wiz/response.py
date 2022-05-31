import season
import io
import json
import os
from werkzeug.routing import Map, Rule

class response:
    def __init__(self, wiz):
        self.wiz = wiz
        self._flask = wiz.server.flask
        self.data = response._data(wiz)
        self.headers = self._headers()
        self.cookies = self._cookies()
        self.status_code = None
        self.mimetype = None
        self.modulename = wiz.modulename
        self.pil_image = self.PIL

    def lang(self, lang):
        self.language(lang)

    def language(self, lang):
        lang = lang[:2].upper()
        self.cookies.set('framework-language', lang)

    def set_status(self, status_code):
        self.status_code = status_code

    def set_mimetype(self, mimetype):
        self.mimetype = mimetype

    def abort(self, code=500):
        self._flask.abort(code)

    def error(self, code=404, response="ERROR"):
        event = season.exception.ResponseException(code=code, response=response)
        raise event
        
    # response functions
    def redirect(self, url):
        self.status_code = 302
        resp = self._flask.redirect(url)
        return self._build(resp)

    def response(self, resp):
        return self._build(resp)

    def PIL(self, pil_image, type='JPEG', mimetype='image/jpeg', as_attachment=False, filename=None):
        img_io = io.BytesIO()
        pil_image.save(img_io, type)
        img_io.seek(0)
        resp = self._flask.send_file(img_io, mimetype=mimetype, as_attachment=as_attachment, attachment_filename=filename)
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
        obj = json.dumps(obj, default=season.util.string.json_default, ensure_ascii=False)
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
        res = json.dumps(res, default=season.util.string.json_default, ensure_ascii=False)
        return self.send(res, content_type='application/json')

    def template(self, template_string, **kwargs):
        wiz = self.wiz
        self.data.set(**kwargs)
        data = self.data.get()
        html = wiz.server.flask.render_template_string(template_string, **data)
        return html

    def render(self, *args, **kwargs):
        wiz = self.wiz
        if len(args) == 0:
            return self

        if len(args) == 1:
            app_id = args[0]
        else:
            route = args[0]
            endpoint = args[1]

            if route is None: return self
            if len(route) == 0: return self
            url_map = []
            if route[-1] == "/":
                url_map.append(Rule(route[:-1], endpoint=endpoint))
            elif route[-1] == ">":
                rpath = route
                while rpath[-1] == ">":
                    rpath = rpath.split("/")[:-1]
                    rpath = "/".join(rpath)
                    url_map.append(Rule(rpath, endpoint=endpoint))
                    if rpath[-1] != ">":
                        url_map.append(Rule(rpath + "/", endpoint=endpoint))
            url_map.append(Rule(route, endpoint=endpoint))
            url_map = Map(url_map)
            url_map = url_map.bind("", "/")

            def matcher(url):
                try:
                    endpoint, kwargs = url_map.match(url, "GET")
                    return endpoint, kwargs
                except:
                    return None, {}
                    
            request_uri = wiz.request.uri()
            app_id, segment = matcher(request_uri)
            wiz.request.segment = season.stdClass(**segment)

        if app_id is None:
            return self

        app = wiz.app(app_id)
        app.use_controller = True
        view = app.view(app_id, **kwargs)

        render_theme = app.data(False)['package']['theme']        
        render_theme = render_theme.split("/")
        themename = render_theme[0]
        layoutname = render_theme[1]

        fs = season.util.os.FileSystem(season.path.lib)
        wizjs = fs.read("wiz.js")
        wizjs = wizjs.replace("{$BASEPATH$}", wiz.server.config.wiz.url)
        view = f'<script type="text/javascript">{wizjs}</script>\n{view}'

        view = wiz.theme(themename).layout(layoutname).view('layout.pug', view)
        
        self.send(view, "text/html")

    # template varialbes
    class _data:
        def __init__(self, wiz):
            self.wiz = wiz
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
                self.data[key] = json.dumps(value, default=season.util.string.json_default, ensure_ascii=False)

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

        event = season.exception.ResponseException(code=response.status_code, response=response)
        raise event
