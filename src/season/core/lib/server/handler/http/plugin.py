import os
from werkzeug.exceptions import HTTPException

import season
from season.core.lib.server.handler.http.base import Base

class Index(Base):
    def route(self, wiz, app, config):
        server = wiz.server
        HTTP_METHODS = config.server.http_method
        wizurl = config.server.wiz_url
        if wizurl[-1] == "/": wizurl = wizurl[:-1]

        @app.route(wizurl, methods=HTTP_METHODS)
        @app.route(wizurl + "/", methods=HTTP_METHODS)
        def wiz_index_handler(*args, **kwargs):
            wiz = season.wiz(server)
            try:
                wiz.trace()
                homeurl = wiz.server.plugin.url(config.wiz.home)
                wiz.response.redirect(homeurl)
            except Exception as e:
                e.wiz = wiz
                raise e


class API(Base):
    def route(self, wiz, app, config):
        server = wiz.server
        HTTP_METHODS = config.server.http_method
        wizurl = config.server.wiz_url
        if wizurl[-1] == "/": wizurl = wizurl[:-1]

        @app.route(wizurl + "/api", methods=HTTP_METHODS)
        @app.route(wizurl + "/api/", methods=HTTP_METHODS)
        @app.route(wizurl + "/api/<path:path>", methods=HTTP_METHODS)
        def wiz_api_handler(*args, **kwargs):
            wiz = season.wiz(server)
            try:
                wiz.trace()
                segment = wiz.match(f"{wizurl}/api/<app_id>/<fnname>/<path:path>")
                if segment is not None:
                    app_id = segment.app_id
                    fnname = segment.fnname
                    wiz.request.segment = segment

                    app = wiz.app(app_id)
                    apifn = app.api()

                    if apifn is None: wiz.response.abort(404)
                    if fnname not in apifn: wiz.response.abort(404)

                    if '__startup__' in apifn:
                        season.util.fn.call(apifn['__startup__'], wiz=wiz)

                    season.util.fn.call(apifn[fnname], wiz=wiz)
            except season.exception.ResponseException as e:
                e.wiz = wiz
                raise e
            except HTTPException as e:
                e.wiz = wiz
                raise e
            except Exception as e:
                e.wiz = wiz
                raise e
            
            wiz.response.abort(404)

        @app.route(wizurl + "/plugin_api", methods=HTTP_METHODS)
        @app.route(wizurl + "/plugin_api/", methods=HTTP_METHODS)
        @app.route(wizurl + "/plugin_api/<path:path>", methods=HTTP_METHODS)
        def wiz_plugin_api_handler(*args, **kwargs):
            wiz = season.wiz(server)
            try:
                wiz.trace()

                # ACL
                aclfn = wiz.server.config.wiz.acl
                if aclfn is not None:
                    season.util.fn.call(aclfn, wiz=wiz)
                    
                config.reload()
                segment = wiz.match(f"{wizurl}/plugin_api/<plugin_id>/<app_id>/<fnname>/<path:path>")
                if segment is not None:
                    plugin_id = segment.plugin_id
                    app_id = segment.app_id
                    fnname = segment.fnname

                    plugin = wiz.server.plugin.load(plugin_id)
                    plugin.trace()
                    plugin.clean()
                    plugin.request.segment = segment

                    app = plugin.app(app_id)
                    apifn = app.api()

                    if apifn is None: wiz.response.abort(404)
                    if fnname not in apifn: wiz.response.abort(404)

                    if '__startup__' in apifn:
                        season.util.fn.call(apifn['__startup__'], wiz=plugin)

                    season.util.fn.call(apifn[fnname], wiz=plugin)
            except season.exception.ResponseException as e:
                e.wiz = wiz
                raise e
            except HTTPException as e:
                e.wiz = wiz
                raise e
            except Exception as e:
                e.wiz = wiz
                raise e
            
            wiz.response.abort(404)

class Resources(Base):
    def route(self, wiz, app, config):
        server = wiz.server
        HTTP_METHODS = config.server.http_method
        wizurl = config.server.wiz_url
        if wizurl[-1] == "/": wizurl = wizurl[:-1]

        @app.route(wizurl + "/resources", methods=HTTP_METHODS)
        @app.route(wizurl + "/resources/", methods=HTTP_METHODS)
        @app.route(wizurl + "/resources/<path:path>", methods=HTTP_METHODS)
        def wiz_resource_handler(*args, **kwargs):
            wiz = season.wiz(server)
            try:
                wiz.trace()

                # find plugin resources
                segment = wiz.match(f"{wizurl}/resources/<plugin_id>/<path:path>")
                plugin_id = segment.plugin_id
                path = segment.path
                filepath = os.path.join(season.path.project, "plugin", 'modules', plugin_id, "resources", path)

                # if not exists, find default theme resources
                if os.path.isfile(filepath) == False:
                    segment = wiz.match(f"{wizurl}/resources/<path:path>")
                    path = segment.path
                    theme = wiz.server.config.wiz.theme
                    filepath = os.path.join(season.path.project, "plugin", 'themes', theme, "resources", path)

                if os.path.isfile(filepath):
                    dirname = os.path.dirname(filepath)
                    filename = os.path.basename(filepath)
                    if wiz.server.config.wiz.build_resource is not None:
                        res = season.util.fn.call(wiz.server.config.wiz.build_resource, wiz=wiz, resource_dirpath=dirname, resource_filepath=filename)
                        if res is not None: return res

                    response = wiz.server.flask.send_from_directory(dirname, filename)
                    raise season.exception.ResponseException(200, response)

                wiz.response.abort(404)
            except season.exception.ResponseException as e:
                e.wiz = wiz
                raise e
            except HTTPException as e:
                e.wiz = wiz
                raise e
            except Exception as e:
                e.wiz = wiz
                raise e

class Router(Base):
    def route(self, wiz, app, config):
        server = wiz.server
        HTTP_METHODS = config.server.http_method
        wizurl = config.server.wiz_url
        if wizurl[-1] == "/": wizurl = wizurl[:-1]

        def menu_generator(menus):
            request = wiz.request
            for menu in menus:
                pt = None
                if 'pattern' in menu: pt = menu['pattern']
                elif 'url' in menu: pt = menu['url']
                if pt is not None:
                    if request.match(pt): menu['class'] = 'active'
                    else: menu['class'] = ''
            return menus

        @app.route(wizurl + "/ui/<path:path>", methods=HTTP_METHODS)
        def wiz_plugin_handler(*args, **kwargs):
            wiz = season.wiz(server)
            try:
                wiz.trace()
                wiz.installed()
                
                # set dev
                dev = wiz.request.query("dev", None)
                if dev is not None:
                    if dev == "false" : wiz.set_dev("false")
                    else: wiz.set_dev("true")
                    wiz.response.redirect(wiz.request.uri())

                # set branch
                branch = wiz.request.query("branch", None)
                if branch is not None and len(branch) > 0:
                    if branch in wiz.branches():
                        wiz.response.cookies.set("season-wiz-branch", branch)
                    wiz.response.redirect(wiz.request.uri())

                # ACL
                aclfn = wiz.server.config.wiz.acl
                if aclfn is not None:
                    season.util.fn.call(aclfn, wiz=wiz)

                # find plugin route
                config.reload()
                segment = wiz.match(f"{wizurl}/ui/<plugin_id>/<path:path>")
                if segment is None: segment = wiz.match(f"{wizurl}/ui/<plugin_id>/")
                if segment is None: segment = wiz.match(f"{wizurl}/ui/<plugin_id>")

                if segment is not None:
                    plugin_id = segment.plugin_id
                    wiz.request.segment = segment

                    # set plugin
                    plugin = wiz.server.plugin.load(plugin_id)
                    plugin.trace()
                    plugin.clean()

                    # set default data
                    plugin.response.data.set(branch=wiz.branch(), branches=wiz.branches(), is_dev=wiz.is_dev())

                    # set menu
                    plugins = wiz.server.config.wiz.plugin
                    navbar = []
                    for plugin_id in plugins:
                        pmenu = plugin.load(plugin_id).config().menu
                        for i in range(len(pmenu)):
                            try:
                                if pmenu[i]['url'][0] != '/': pmenu[i]['url'] = wizurl + "/ui/" + plugin_id + "/" + pmenu[i]['url']
                                else: pmenu[i]['url'] = wizurl + "/ui/" + plugin_id + pmenu[i]['url']
                            except:
                                pass
                        navbar = navbar + pmenu
                    navbar = menu_generator(navbar)
                    plugin.response.data.set(navbar=navbar)

                    # routing
                    path = plugin.request.uri()
                    if len(path) == 0: path = "/"
                    app, segment = plugin.route.match(path)

                    if app is not None:
                        plugin.request.segment = season.stdClass(**segment)
                        app.proceed()
                
                wiz.response.abort(404)
            except season.exception.ResponseException as e:
                e.wiz = wiz
                raise e
            except HTTPException as e:
                e.wiz = wiz
                raise e
            except Exception as e:
                e.wiz = wiz
                raise e
            
            wiz.response.abort(404)
