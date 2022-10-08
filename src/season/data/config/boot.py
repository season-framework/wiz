def bootstrap(app, config):
    pass

secret_key = "season-wiz-secret"

socketio = dict()
socketio['cors_allowed_origins'] = '*'
socketio['async_handlers'] = True
socketio['always_connect'] = False
socketio['manage_session'] = True

run = dict()
run['host'] = "0.0.0.0"
run['port'] = __PORT__
run['use_reloader'] = False