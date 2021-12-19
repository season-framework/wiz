import logging
import os
import time
import traceback
import inspect
import flask
import flask_socketio
from werkzeug.exceptions import HTTPException

class stdClass(dict):
    def __init__(self, *args, **kwargs):
        super(stdClass, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        self[k] = stdClass(v)
                    else:
                        self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    self[k] = stdClass(v)
                else:
                    self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(stdClass, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(stdClass, self).__delitem__(key)
        del self.__dict__[key]

class bootstrap:
    def __init__(self, season):
        self.response = None
        self.season = season

    def bootstrap(self, ismain):
        season = self.season
        boottime = season.boottime
        app = flask.Flask('__main__', static_url_path='')
        socketio = flask_socketio.SocketIO(app)

        HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']
        season = self.season
        season.core.build.template()

        log = logging.getLogger('werkzeug')
        log.disabled = True
        app.logger.disabled = True
        os.environ["WERKZEUG_RUN_MAIN"] = "true"

        def init_error_info(default="unknown"):
            ERROR_INFO = stdClass()
            ERROR_INFO.path = default
            ERROR_INFO.module = default
            ERROR_INFO.modulepath = default
            ERROR_INFO.controllerpath = default
            ERROR_INFO.segmentpath = default
            return ERROR_INFO
        
        # Handler
        config = season.config.load()
        host = config.get("host", "0.0.0.0")
        port = int(config.get("port", 3000))

        handler = stdClass()
        handler.onerror = config.get('on_error', None)
        handler.before_request = config.get('before_request', None)
        handler.after_request = config.get('after_request', None)
        handler.build = config.get('build', None)
        handler.build_resource = config.get('build_resource', None)
        handler.handle_resource = config.get('handle_resource', None)

        LOG_DEBUG = 0
        LOG_INFO = 1
        LOG_DEV = 2
        LOG_WARNING = 3
        LOG_ERROR = 4
        LOG_CRITICAL = 5
        LOG_LEVEL = config.get('log_level', LOG_ERROR)

        def _logger(level, ERROR_INFO=None, message=None, code=200, starttime=None):
            if starttime is not None: starttime = round(time.time() * 1000) - starttime
            if LOG_LEVEL > level: return
            _prefix = ""
            _prefix_color = ""
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            if level == LOG_DEBUG: 
                _prefix_color = "\033[94m"
                _prefix = "[DEBUG]"
            if level == LOG_INFO: 
                _prefix_color = "\033[94m"
                _prefix = "[INFO_]"
            if level == LOG_DEV: 
                _prefix_color = "\033[93m"
                _prefix = "[DEV__]"
            if level == LOG_WARNING: 
                _prefix_color = "\033[93m"
                _prefix = "[WARN_]"
            if level == LOG_ERROR: 
                _prefix_color = "\033[91m"
                _prefix = "[ERROR]"
            if level == LOG_CRITICAL: 
                _prefix_color = "\033[91m"
                _prefix = "[CRITI]"

            sourcefile = "unknown"
            try:
                for stack in inspect.stack():
                    try:
                        if stack.filename[:len(season.core.PATH.PROJECT)] == season.core.PATH.PROJECT:
                            sourcefile = stack.filename[len(season.core.PATH.PROJECT)+1:]
                            break
                    except:
                        pass
                if sourcefile == 'unknown' and ERROR_INFO.controllerpath != 'unknown':
                    sourcefile = ERROR_INFO.controllerpath
            except:
                pass

            print_res = f"{_prefix_color}{_prefix}[{timestamp}]"
            if level == LOG_DEV:
                print_res = f"{_prefix_color}{_prefix}"
                if ERROR_INFO is not None:
                    print_res = print_res + f"[{sourcefile}]"
                if starttime is not None:
                    print_res = print_res + f"[{starttime}ms]"
                print_res = print_res + "\033[0m " + message
            else:
                print_res = print_res + f"[{code}]"
                if starttime is not None:
                    print_res = print_res + f"[{starttime}ms]"
                print_res = print_res + "\033[0m "
                try:
                    print_res = print_res + str(ERROR_INFO.path)
                except:
                    pass

            print_res = [print_res]
            if level >= LOG_ERROR:
                print_res.append(f"{_prefix_color}[TRACEBACK][SRCPATH]\033[0m " + sourcefile)
            if message is not None and level != LOG_DEV: 
                print_res.append(f"[TRACEBACK][MESSAGE] " + message)
            if level == LOG_ERROR: 
                print_res.append(traceback.format_exc())
            print_res = "\n".join(print_res).strip()
            print(print_res)
        
        app.jinja_env.variable_start_string = config.get("jinja_variable_start_string", "{{")
        app.jinja_env.variable_end_string = config.get("jinja_variable_end_string", "}}")
        app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')
        
        # response handler
        @app.errorhandler(season.core.CLASS.RESPONSE.STATUS)
        def handle_response(e):
            response, status_code = e.get_response()
            return response, status_code

        # Exception Handler 
        @app.errorhandler(HTTPException)
        def handle_exception_http(e):
            return e.get_response()

        @app.errorhandler(Exception)
        def handle_exception(e):
            return '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><title>500 Internal Server Error</title><h1>Internal Server Error</h1><p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>', 500

        # Before Request
        @app.before_request
        def before_request():
            if handler.before_request is not None:
                handler.before_request(season)

        @app.after_request
        def after_request(response):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            response.headers['Cache-Control'] = 'public, max-age=0'
            if handler.after_request is not None:
                res = handler.after_request(response)
                if res is not None: return res
            return response

        @app.route('/resources/<path:path>')
        def resources(path=''):
            starttime = round(time.time() * 1000)
            ERROR_INFO = init_error_info()

            try:
                ERROR_INFO.path = f"/resources/{path}"

                if handler.handle_resource is not None:
                    framework = season.core.CLASS.FRAMEWORK(season=season, module="", module_path="", controller_path="", segment_path="", ERROR_INFO=ERROR_INFO, logger=_logger, flask=flask, socketio=socketio, flask_socketio=flask_socketio)
                    res = handler.handle_resource(framework, path)
                    if res is not None: 
                        _logger(LOG_DEBUG, ERROR_INFO=ERROR_INFO, starttime=starttime)
                        return res

                path = path.split('/')

                # check module resource
                for i in range(len(path)):
                    idx = len(path) - i
                    module = "/".join(path[:idx])
                    resource_filepath = "/".join(path[idx:])
                    resource_dirpath = os.path.join(season.core.PATH.WEBSRC, 'modules', module, 'resources')
                    if os.path.isfile(os.path.join(resource_dirpath, resource_filepath)):
                        if handler.build_resource is not None:
                            res = handler.build_resource(resource_dirpath, resource_filepath)
                            if res is not None: return res
                        _logger(LOG_DEBUG, ERROR_INFO=ERROR_INFO, starttime=starttime)
                        return flask.send_from_directory(resource_dirpath, resource_filepath)
                
                # global resource
                resource_abspath = os.path.join(season.core.PATH.WEBSRC, 'resources', "/".join(path))
                if os.path.isfile(resource_abspath):
                    resource_filepath = os.path.basename(resource_abspath)
                    resource_dirpath = os.path.dirname(resource_abspath)
                    if handler.build_resource is not None:
                        res = handler.build_resource(resource_dirpath, resource_filepath)
                        if res is not None: return res
                    _logger(LOG_DEBUG, ERROR_INFO=ERROR_INFO, starttime=starttime)
                    return flask.send_from_directory(resource_dirpath, resource_filepath)

                flask.abort(404)
            except season.core.CLASS.RESPONSE.STATUS as e:
                _logger(LOG_DEBUG, ERROR_INFO=ERROR_INFO, starttime=starttime)
                raise e
            except HTTPException as e:
                _logger(LOG_WARNING, ERROR_INFO=ERROR_INFO, code=e.code, starttime=starttime)
                raise e
            except Exception as e:
                _logger(LOG_ERROR, ERROR_INFO=ERROR_INFO, code=500, starttime=starttime)
                raise e

        @app.route("/", methods=HTTP_METHODS)
        @app.route("/<string:module>", methods=HTTP_METHODS)
        @app.route("/<string:module>/", methods=HTTP_METHODS)
        @app.route("/<string:module>/<path:path>", methods=HTTP_METHODS)
        def catch_all(module='', path=''):
            starttime = round(time.time() * 1000)
            ERROR_INFO = init_error_info()
            try:
                path = f"{module}/{path}"
                ERROR_INFO.path = "/"
                if path != "/": ERROR_INFO.path = "/" + path
                path = path.split('/')
                
                # module finder
                def module_finder():
                    for i in range(len(path)):
                        idx = len(path) - i
                        module = "/".join(path[:idx])
                        module_path = os.path.join(season.core.PATH.MODULES, module)
                        uri_path = path[idx:]

                        for j in range(len(uri_path)):
                            uri_idx = len(uri_path) - j
                            controller_namespace = "/".join(uri_path[:uri_idx])
                            segment_path = "/".join(uri_path[uri_idx:])

                            controller_path = os.path.join(module_path, 'controller', controller_namespace, 'index.py')
                            if os.path.isfile(controller_path):
                                return module, module_path, controller_path, segment_path

                            controller_path = os.path.join(module_path, 'controller', controller_namespace + '.py')
                            if os.path.isfile(controller_path):
                                return module, module_path, controller_path, segment_path
                        
                        controller_path = os.path.join(module_path, 'controller', 'index.py')
                        if os.path.isfile(controller_path):
                            return module, module_path, controller_path, "/".join(uri_path)
                            
                    return "", "", "", ""

                module, module_path, controller_path, segment_path = module_finder()

                framework = season.core.CLASS.FRAMEWORK(season=season, module=module, module_path=module_path, controller_path=controller_path, segment_path=segment_path, ERROR_INFO=ERROR_INFO, logger=_logger, flask=flask, socketio=socketio, flask_socketio=flask_socketio)

                # load config
                config = framework.config.load()

                # build controller
                controller = None
                fnname = segment_path.split('/')[0]
                if os.path.isfile(controller_path):
                    file = open(controller_path, mode="rb")
                    ctrlcode = file.read().decode('utf-8')
                    file.close()
                    _tmp = {'__file__': controller_path}
                    exec(compile(ctrlcode, controller_path, 'exec'), _tmp)
                    try:
                        controller = _tmp['Controller'](framework)
                    except:
                        controller = _tmp['Controller']()
                    if hasattr(controller, fnname):
                        segment_path = segment_path[len(fnname)+1:]
                        fnname = fnname
                    elif hasattr(controller, '__default__'):
                        fnname = '__default__'
                    elif hasattr(controller, '__index__'):
                        fnname = '__index__'
                framework.segmentpath = segment_path

                # process filter
                filters = config.get('filter', [])
                for _filter in filters:
                    filter_path = os.path.join(season.core.PATH.WEBSRC, 'app', 'filter', _filter + '.py')
                    if os.path.isfile(filter_path) == False:
                        continue
                    
                    ERROR_INFO.controllerpath = filter_path

                    file = open(filter_path, mode="rb")
                    _code = file.read().decode('utf-8')
                    file.close()
                    _tmp = {'__file__': filter_path}
                    exec(compile(_code, filter_path, 'exec'), _tmp)
                    filter_fn = _tmp['process']
                    res = filter_fn(framework)
                    if res is not None:
                        return res
                
                # process controller
                ERROR_INFO.controllerpath = controller_path
                if os.path.isfile(controller_path) == False:
                    flask.abort(404)

                if controller is not None:
                    controller.__framework__ = framework
                    if hasattr(controller, '__startup__'):
                        res = getattr(controller, '__startup__')(framework)
                        if res is not None:
                            return res
                    
                    if hasattr(controller, fnname):
                        return getattr(controller, fnname)(framework)
                        
                flask.abort(404)

            except season.core.CLASS.RESPONSE.STATUS as e:
                _logger(LOG_INFO, ERROR_INFO=ERROR_INFO, starttime=starttime)
                raise e

            except HTTPException as e:
                try:
                    if hasattr(controller, '__error__'):
                        getattr(controller, '__error__')(framework, e)
                except season.core.CLASS.RESPONSE.STATUS as e2:
                    raise e2
                except HTTPException as e2:
                    _logger(LOG_WARNING, ERROR_INFO=ERROR_INFO, code=e2.code, starttime=starttime)
                    raise e2
                except Exception as e2:
                    _logger(LOG_ERROR, ERROR_INFO=ERROR_INFO, code=500, starttime=starttime)
                    raise e2

                try:
                    if handler.onerror is not None:
                        handler.onerror(framework, e)
                except season.core.CLASS.RESPONSE.STATUS as e2:
                    raise e2
                except HTTPException as e2:
                    _logger(LOG_WARNING, ERROR_INFO=ERROR_INFO, code=e2.code, starttime=starttime)
                    raise e2
                except Exception as e2:
                    _logger(LOG_ERROR, ERROR_INFO=ERROR_INFO, code=500, starttime=starttime)
                    raise e2

                _logger(LOG_WARNING, ERROR_INFO=ERROR_INFO, code=e.code, starttime=starttime)
                raise e

            except Exception as e:
                try:
                    if hasattr(controller, '__error__'):
                        getattr(controller, '__error__')(framework, e)
                except season.core.CLASS.RESPONSE.STATUS as e2:
                    raise e2
                except HTTPException as e2:
                    _logger(LOG_WARNING, ERROR_INFO=ERROR_INFO, code=e2.code, starttime=starttime)
                    raise e2
                except Exception as e2:
                    _logger(LOG_ERROR, ERROR_INFO=ERROR_INFO, code=500, starttime=starttime)
                    raise e2
                
                try:
                    if handler.onerror is not None:
                        handler.onerror(framework, e)
                except season.core.CLASS.RESPONSE.STATUS as e2:
                    raise e2
                except HTTPException as e2:
                    _logger(LOG_WARNING, ERROR_INFO=ERROR_INFO, code=e2.code, starttime=starttime)
                    raise e2
                except Exception as e2:
                    _logger(LOG_ERROR, ERROR_INFO=ERROR_INFO, code=500, starttime=starttime)
                    raise e2

                _logger(LOG_ERROR, ERROR_INFO=ERROR_INFO, code=500, starttime=starttime)
                raise e

        # socket io
        @socketio.on_error_default
        def socketio_error_handler(e):
            _logger(LOG_ERROR, "socket error")
            return

        def socket_finder():
            result = dict()
            for root, _, files in os.walk(season.core.PATH.MODULES):
                if root.split("/")[-1] == "socket":
                    module_path = "/".join(root.split("/")[:-1])
                    module = module_path[len(season.core.PATH.MODULES) + 1:]
                    ERROR_INFO = init_error_info()
                    
                    for fname in files:
                        _fname, ext = os.path.splitext(fname)
                        if ext != ".py": continue
                        controller_path = os.path.join(root, fname)
                        eventname = module
                        if fname != 'index.py':
                            eventname = os.path.join(module, _fname)
                        framework = season.core.CLASS.FRAMEWORK(season=season, module=module, module_path=module_path, controller_path=controller_path, segment_path="", ERROR_INFO=ERROR_INFO, logger=_logger, flask=flask, socketio=socketio, flask_socketio=flask_socketio)

                        file = open(controller_path, mode="rb")
                        ctrlcode = file.read().decode('utf-8')
                        file.close()
                        _tmp = {'__file__': controller_path}
                        exec(compile(ctrlcode, controller_path, 'exec'), _tmp)
                        try:
                            controller = _tmp['Controller'](framework)
                        except:
                            controller = _tmp['Controller']()
                        result[eventname] = stdClass()
                        result[eventname].controller = controller
                        result[eventname].framework = framework
            return result
                        
        sockets = socket_finder()
        for eventname in sockets:
            controller = sockets[eventname].controller
            framework = sockets[eventname].framework
            namespace =  "/" + eventname

            if hasattr(controller, 'register'):
                fnlist = controller.register
            else:
                fnlist = dir(controller)

            def regist(controller, fnname, framework, namespace):
                if hasattr(getattr(controller, fnname), '__call__') == False:
                    return False

                startup = None
                if hasattr(controller, '__startup__'):
                    startup = getattr(controller, '__startup__')

                def _socketwrap(controller, fnname, framework, namespace):
                    def socketwrap(*args):
                        def emit(*args, **kwargs):
                            kwargs['namespace'] = namespace
                            socketio.emit(*args, **kwargs)
                            
                        def send(message, **kwargs):
                            kwargs['namespace'] = namespace
                            socketio.send(message, **kwargs)
                        
                        def join_room(room, sid=None):
                            socketio.join_room(room, sid=sid, namespace=namespace)
                        
                        def leave_room(room, sid=None):
                            socketio.leave_room(room, sid=sid, namespace=namespace)

                        framework.socket = stdClass()
                        framework.socket.emit = emit
                        framework.socket.send = send
                        framework.socket.join_room = join_room
                        framework.socket.leave_room = leave_room

                        data = None
                        if len(args) == 1:
                            data = args[0]
                        elif len(args) > 1:
                            data = args

                        try:
                            if startup is not None: startup(framework, namespace)
                        except:
                            if startup is not None: startup(framework)

                        try:
                            getattr(controller, fnname)(framework, namespace, data)
                        except:
                            getattr(controller, fnname)(framework, data)

                    return socketwrap

                socketio.on_event(fnname, _socketwrap(controller, fnname, framework, namespace), namespace=namespace)
                return True

            reglist = []
            for fnname in fnlist:
                if fnname.startswith("__") and fnname.endswith("__"): continue
                if regist(controller, fnname, framework, namespace):
                    reglist.append(fnname)
            reglist = "/".join(reglist)
            _logger(LOG_DEV, message=f"socketio event binding on '{reglist}' with namespace '{namespace}'")
                
            if hasattr(controller, 'namespaces'):
                namespaces = controller.namespaces
                for _namespace in namespaces:
                    controller = namespaces[_namespace]
                    _namespace = os.path.join(namespace, _namespace)
                    if hasattr(controller, 'register'):
                        fnlist = controller.register
                    else:
                        fnlist = dir(controller)

                    reglist = []
                    for fnname in fnlist:
                        if fnname.startswith("__") and fnname.endswith("__"): continue
                        if regist(controller, fnname, framework, _namespace):
                            reglist.append(fnname)
                    reglist = "/".join(reglist)
                    _logger(LOG_DEV, message=f"socketio event binding on '{reglist}' with namespace '{_namespace}'")

        app.framework = season.core.CLASS.FRAMEWORK(season=season, module="build", module_path="build", controller_path="", segment_path="", ERROR_INFO=init_error_info("build"), logger=_logger, flask=flask, socketio=socketio, flask_socketio=flask_socketio)

        if handler.build is not None:
            try:
                _app = handler.build(app, socketio)
            except:
                _app = handler.build(app)
            if _app is not None:
                app = app
        
        if ismain:
            _logger(LOG_DEV, message=f"running on http://{host}:{port}/ (Press CTRL+C to quit)")
            socketio.run(app, host=host, port=port)

        return app, socketio