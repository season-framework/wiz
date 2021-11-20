import logging
import flask
import os
import lesscpy
from six import StringIO
import season

config = season.stdClass()

config.host = "0.0.0.0"
config.port = 3000

config.log_level = season.LOG_INFO

config.filter = [
    'indexfilter'
]

# Regist error handler

# def onError(framework, e):
#     framework.response.redirect("/")
# config.on_error = onError


# process before request

# def beforeRequest(framework):
#     pass
# config.before_request = beforeRequest


# process after request, like add http header

# def afterRequest(response):
#     return response
# config.after_request = afterRequest


# additional build app
def build(app):
    app.secret_key = "session-secret"
    
config.build = build

# regist resource handler
resources_cache = dict()
def build_resource(resource_dirpath, resource_filepath):
    _, ext = os.path.splitext(resource_filepath)
    filepath = os.path.join(resource_dirpath, resource_filepath)
    if filepath in resources_cache:
        return resources_cache[filepath]
    
    if ext == '.less':
        f = open(filepath, 'r')
        lessfile = f.read()
        f.close()
        cssfile = lesscpy.compile(StringIO(lessfile), minify=True)
        response = flask.Response(str(cssfile))
        response.headers['Content-Type'] = 'text/css'
        resources_cache[filepath] = response
        return resources_cache[filepath]

config.build_resource = build_resource