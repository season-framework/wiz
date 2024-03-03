import os
import season

class Logger:
    LOG_DEBUG = 0
    LOG_INFO = 1
    LOG_WARN = LOG_WARNING = 2
    LOG_DEV = 3
    LOG_ERR = LOG_ERROR = 4
    LOG_CRIT = LOG_CRITICAL = 5

    def __init__(self, wiz, *tags):        
        def trigger(logdata):
            if wiz.server.config.boot.log is not None:
                try:
                    logpath = os.path.join(wiz.server.path.root, wiz.server.config.boot.log)
                    if os.path.exists(logpath) == False:
                        f = open(logpath, "w")
                        f.write("")
                        f.close()
                    f = open(logpath, "a")
                    f.write(logdata + "\n")
                    f.close()
                except:
                    pass
            else:
                print(logdata)
            
            try:
                if wiz is not None and wiz.project.dev():
                    project = wiz.project()
                    wiz.server.app.socketio.emit("log", logdata + "\n", namespace=wiz.uri.ide("ide"), to=project)
            except Exception as e:
                pass

        self.log = season.util.Logger(*tags, level=wiz.server.config.boot.log_level, trigger=trigger)

    def __call__(self, *args, level=LOG_DEV):
        self.log(*args, level=level)
