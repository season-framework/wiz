import season
import io
import json
import os
import re
from abc import *

# internal classes
class Headers:
    def __init__(self):
        self.headers = {}
    
    def get(self, name=None):
        if name is None:
            return self.headers
        if name in self.headers:
            return self.headers[name]
        return None

    def set(self, **kwargs):
        for key, value in kwargs.items():
            self.headers[key] = value

    def clear(self):
        self.headers = {}

class Cookies:
    def __init__(self):
        self.cookies = {}
    
    def get(self, name=None):
        if name is None:
            return self.cookies
        if name in self.cookies:
            return self.cookies[name]
        return None

    def set(self, **kwargs):
        for key, value in kwargs.items():
            self.cookies[key] = value

    def clear(self):
        self.cookies = {}

class Data:
    def __init__(self):
        self.data = dict()
    
    def get(self, key=None):
        if key is None:
            return self.data
        if key in self.data:
            return self.data[key]
        return None

    def set(self, **kwargs):
        for key, value in kwargs.items():
            self.data[key] = value

    def set_json(self, **kwargs):
        for key, value in kwargs.items():
            self.data[key] = json.dumps(value, default=season.util.string.json_default, ensure_ascii=False)

    def clear(self):
        self.data = dict()

class Response(metaclass=ABCMeta):
    def __init__(self, wiz):
        self.wiz =  wiz
        self._flask = wiz.server.package.flask
        self.data = Data()
        self.headers = Headers()
        self.cookies = Cookies()
        self.status_code = None
        self.mimetype = None
        self.pil_image = self.PIL
    
    def redirect(self, url):
        url = self.wiz.uri.base(url)
        self.status_code = 302
        resp = self._flask.redirect(url)
        return self._build(resp)

    def lang(self, lang):
        self.language(lang)

    def language(self, lang):
        lang = lang[:2].upper()
        self.cookies.set(**{'framework-language':lang})

    def set_status(self, status_code):
        self.status_code = status_code

    def set_mimetype(self, mimetype):
        self.mimetype = mimetype

    def abort(self, code=500):
        self._flask.abort(code)

    def error(self, code=404, response="ERROR"):
        event = season.lib.exception.ResponseException(code=code, response=response)
        raise event
    
    def response(self, resp):
        return self._build(resp)

    def PIL(self, pil_image, type='JPEG', mimetype='image/jpeg', as_attachment=False, filename=None):
        img_io = io.BytesIO()
        pil_image.save(img_io, type)
        img_io.seek(0)
        resp = None
        try: resp = self._flask.send_file(img_io, mimetype=mimetype, as_attachment=as_attachment, attachment_filename=filename)
        except: resp = None
        if resp is None:
            try: resp = self._flask.send_file(img_io, mimetype=mimetype, as_attachment=as_attachment, download_name=filename)
            except: pass
        return self._build(resp)

    def download(self, filepath, as_attachment=True, filename=None):
        if os.path.isfile(filepath):
            resp = None
            try: resp = self._flask.send_file(filepath, as_attachment=as_attachment, attachment_filename=filename)
            except: resp = None
            if resp is None:
                try: resp = self._flask.send_file(filepath, as_attachment=as_attachment, download_name=filename)
                except: pass
            return self._build(resp)
        self._flask.abort(404)
    
    def stream(self, filepath, rangeHeader=None, mimetype='video/mp4', content_type=None, direct_passthrough=True):
        if content_type is None: content_type = mimetype
        self.headers.set(**{'Accept-Ranges': 'bytes'})

        def get_chunk(byte1=None, byte2=None):
            file_size = os.stat(filepath).st_size
            start = 0
            
            if byte1 < file_size:
                start = byte1
            if byte2:
                length = byte2 + 1 - byte1
            else:
                length = file_size - start

            with open(filepath, 'rb') as f:
                f.seek(start)
                chunk = f.read(length)
            return chunk, start, length, file_size

        byte1, byte2 = 0, None
        if rangeHeader:
            match = re.search(r'(\d+)-(\d*)', rangeHeader)
            groups = match.groups()

            if groups[0]:
                byte1 = int(groups[0])
            if groups[1]:
                byte2 = int(groups[1])

        chunk, start, length, file_size = get_chunk(byte1, byte2)
        
        resp = self._flask.Response(chunk, 206, mimetype=mimetype, content_type=content_type, direct_passthrough=direct_passthrough)
        self.headers.set(**{'Content-Range': 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size)})
        self.set_status(206)
        return self._build(resp)
    
    def send(self, message, content_type=None):
        resp = self._flask.Response(str(message))
        if content_type is not None:
            self.headers.set(**{'Content-Type': content_type})
        return self._build(resp)

    def json(self, obj):
        try:
            obj = dict(obj)
        except:
            pass
        obj = json.dumps(obj, default=season.util.string.json_default, ensure_ascii=False)
        resp = self._flask.Response(str(obj))
        self.headers.set(**{'Content-Type': 'application/json'})
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

        event = season.lib.exception.ResponseException(code=response.status_code, response=response)
        raise event
