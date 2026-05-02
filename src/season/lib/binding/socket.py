import os
import season
import traceback

class SocketHandler:
    def __init__(self, server, namespace):
        self.server = server
        self.namespace = namespace
    
    def emit(self, *args, **kwargs):
        socketio = self.server.app.socketio
        kwargs['namespace'] = self.namespace
        socketio.emit(*args, **kwargs)

    def send(self, message, **kwargs):
        socketio = self.server.app.socketio
        kwargs['namespace'] = self.namespace
        socketio.send(message, **kwargs)
    
    def join_room(self, room, sid=None):
        self.join(room, sid=sid)

    def join(self, room, sid=None):
        socketio = self.server.package.flask_socketio
        socketio.join_room(room, sid=sid, namespace=self.namespace)

    def leave_room(self, room, sid=None):
        self.leave(room, sid=sid)

    def leave(self, room, sid=None):
        socketio = self.server.package.flask_socketio
        socketio.leave_room(room, sid=sid, namespace=self.namespace)

    def status(self, channel='message', to=None, **msg):
        if 'type' not in msg: msg['type'] = 'status'
        acts = dict()
        if to is not None: acts['to'] = to
        self.emit(channel, msg, **acts)

    def clients(self, room):
        sio = self.server.app.socketio.server
        clients = sio.manager.get_participants(self.namespace, room)
        clients = list(clients)
        return clients

    def rooms(self):
        sio = self.server.app.socketio.server
        rooms = []
        for room_name, room in sio.manager.rooms[self.namespace].items():
            rooms.append(room_name)
        return rooms

class IdeController:
    def __init__(self, server):
        self.server = server

    def connect(self):
        pass

    def join(self, flask, data, io):
        sid = flask.request.sid
        if 'id' not in data: return
        room = data['id']
        io.join(room)

    def leave(self, flask, data, io):
        sid = flask.request.sid
        if 'id' not in data: return
        room = data['id']
        io.leave(room)

    def disconnect(self, flask, io):
        sid = flask.request.sid

class Socket:
    def __init__(self, server):
        self.server = server
        self.socketio = server.app.socketio
        self.registry = dict()
        server.app.socketio_binding = self

        self._bind_error_handler()
        if server.config.boot.bundle == False:
            self.bind_ide()
        self.bind_projects()

    def createWiz(self):
        return season.lib.core.Wiz(self.server)

    def _bind_error_handler(self):
        socketio = self.socketio

        @socketio.on_error_default
        def sio_handle_exception_error(e):
            wiz = self.createWiz()
            logger = wiz.logger("ide", "sock", "error")
            errormsg = traceback.format_exc()
            logger(errormsg, level=season.LOG_ERROR)

    def wrapper(self, fn, namespace):
        server = self.server

        def proceed(*args, **kwargs):
            data = None
            if len(args) == 1: data = args[0]
            elif len(args) > 1: data = args

            params = dict()
            params['server'] = server
            params['wiz'] = self.createWiz()
            params['socketio'] = server.app.socketio
            params['flask_socketio'] = server.package.flask_socketio
            params['flask'] = server.package.flask
            params['io'] = SocketHandler(server, namespace)
            params['data'] = data

            season.util.compiler(fn).call(**params)

        return proceed

    def _namespace_for_ide_app(self, wiz, app_id):
        return wiz.uri.ide("ide") + f"/app/{app_id}"

    def _namespace_for_project_app(self, wiz, project, app_id):
        return wiz.uri.ide() + f"/app/{project}/{app_id}"

    def _load_controller(self, fs, socketiofile, logger, wiz):
        if fs.exists(socketiofile) == False:
            return None

        code = fs.read(socketiofile)
        siopath = fs.abspath(socketiofile)
        if len(code) == 0:
            return None

        ctrl = season.util.compiler().build(code, name=siopath, logger=logger, wiz=wiz).fn
        ctrl = ctrl['Controller']
        return season.util.compiler(ctrl).call(
            server=self.server,
            wiz=wiz,
            socketio=self.server.app.socketio,
            flask_socketio=self.server.package.flask_socketio,
            flask=self.server.package.flask
        )

    def _controller_events(self, ctrl):
        events = []
        for fnname in dir(ctrl):
            if fnname.startswith("__") and fnname.endswith("__"): continue
            fn = getattr(ctrl, fnname)
            if callable(fn) == False: continue
            events.append((fnname, fn))
        return events

    def _unbind_namespace(self, namespace):
        handlers = self.socketio.server.handlers
        if namespace in handlers:
            del handlers[namespace]
        if namespace in self.registry:
            del self.registry[namespace]

    def _unbind_missing_project_apps(self, project, app_ids):
        app_ids = set(app_ids)
        for namespace, info in list(self.registry.items()):
            if info.get('source') != 'project': continue
            if info.get('project') != project: continue
            if info.get('app_id') in app_ids: continue
            self._unbind_namespace(namespace)

    def _unbind_missing_ide_apps(self, app_ids):
        app_ids = set(app_ids)
        for namespace, info in list(self.registry.items()):
            if info.get('source') != 'ide': continue
            if info.get('app_id') in app_ids: continue
            self._unbind_namespace(namespace)

    def _register_controller(self, namespace, ctrl, logger=None, **meta):
        events = self._controller_events(ctrl)
        if len(events) == 0:
            self._unbind_namespace(namespace)
            return False

        self._unbind_namespace(namespace)
        for fnname, fn in events:
            proceed = self.wrapper(fn, namespace)
            self.socketio.on_event(fnname, proceed, namespace=namespace)

        meta['events'] = [fnname for fnname, fn in events]
        self.registry[namespace] = meta

        if logger is not None:
            logger(f"socketio binded: `{namespace}`", level=season.LOG_INFO)
        return True

    def bind_ide_default(self):
        wiz = self.createWiz()
        namespace = wiz.uri.ide("ide")
        ctrl = IdeController(self.server)
        logger = wiz.logger("ide", "sock")
        return self._register_controller(namespace, ctrl, logger=logger, source='ide-default')

    def bind_ide_app(self, app_id, wiz=None, fs=None, logger=None, rebind=False):
        if wiz is None:
            wiz = self.createWiz()
        if fs is None:
            fs = wiz.ide.fs("app")
        if logger is None:
            logger = wiz.logger("ide", "sock", "app")

        namespace = self._namespace_for_ide_app(wiz, app_id)
        socketiofile = os.path.join(app_id, 'socket.py')

        try:
            ctrl = self._load_controller(fs, socketiofile, logger, wiz)
            if ctrl is None:
                if rebind: self._unbind_namespace(namespace)
                return False

            return self._register_controller(
                namespace,
                ctrl,
                logger=logger,
                source='ide',
                app_id=app_id,
                socketiofile=fs.abspath(socketiofile)
            )
        except Exception:
            logger(f"`{app_id}` socketio file not binded at ide:\n" + traceback.format_exc(), level=season.LOG_ERROR)
            return False

    def bind_ide(self):
        self.bind_ide_default()

        wiz = self.createWiz()
        fs = wiz.ide.fs("app")
        logger = wiz.logger("ide", "sock", "app")
        apps = fs.ls()
        for app_id in apps:
            self.bind_ide_app(app_id, wiz=wiz, fs=fs, logger=logger)

    def rebind_ide(self, app_id=None):
        self.server.cache.clear()

        if app_id is not None:
            return self.bind_ide_app(app_id, rebind=True)

        wiz = self.createWiz()
        fs = wiz.ide.fs("app")
        logger = wiz.logger("ide", "sock", "app")
        apps = fs.ls()
        for target in apps:
            self.bind_ide_app(target, wiz=wiz, fs=fs, logger=logger, rebind=True)
        self._unbind_missing_ide_apps(apps)
        return apps

    def bind_project_app(self, project, app_id, wiz=None, fs=None, logger=None, rebind=False):
        if wiz is None:
            wiz = self.createWiz()
            wiz.project(project)
        if fs is None:
            fs = wiz.project.fs("bundle", "src", "app")
        if logger is None:
            logger = wiz.logger("sock")

        namespace = self._namespace_for_project_app(wiz, project, app_id)
        socketiofile = os.path.join(app_id, 'socket.py')

        try:
            ctrl = self._load_controller(fs, socketiofile, logger, wiz)
            if ctrl is None:
                if rebind: self._unbind_namespace(namespace)
                return False

            return self._register_controller(
                namespace,
                ctrl,
                logger=logger,
                source='project',
                project=project,
                app_id=app_id,
                socketiofile=fs.abspath(socketiofile)
            )
        except Exception:
            logger(f"`{app_id}` socketio file not binded at `{project}` project:\n" + traceback.format_exc(), level=season.LOG_ERROR)
            return False

    def bind_project(self, project):
        wiz = self.createWiz()
        wiz.project(project)
        fs = wiz.project.fs("bundle", "src", "app")
        logger = wiz.logger("sock")
        apps = fs.list()

        for app_id in apps:
            self.bind_project_app(project, app_id, wiz=wiz, fs=fs, logger=logger)
        return apps

    def bind_projects(self):
        wiz = self.createWiz()
        projects = wiz.project.list()
        if self.server.config.boot.bundle:
            projects = ["main"]

        for project in projects:
            self.bind_project(project)
        return projects

    def rebind_project(self, project=None, app_id=None):
        self.server.cache.clear()

        if project is None:
            wiz = self.createWiz()
            project = wiz.project.list()
            if self.server.config.boot.bundle:
                project = ["main"]
        elif type(project) != list:
            project = [project]

        result = dict()
        for target_project in project:
            if app_id is not None:
                result[target_project] = self.bind_project_app(target_project, app_id, rebind=True)
                continue

            wiz = self.createWiz()
            wiz.project(target_project)
            fs = wiz.project.fs("bundle", "src", "app")
            logger = wiz.logger("sock")
            apps = fs.list()

            for target_app_id in apps:
                self.bind_project_app(target_project, target_app_id, wiz=wiz, fs=fs, logger=logger, rebind=True)

            self._unbind_missing_project_apps(target_project, apps)
            result[target_project] = apps

        return result
