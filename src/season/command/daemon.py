import os
import sys
from argh import arg
import time
import psutil
import platform
import signal
import atexit
import multiprocessing as mp
import importlib
import season

PATH_WEBSRC = os.getcwd()
PATH_PUBLIC = os.path.join(PATH_WEBSRC, 'public')
PATH_APP = os.path.join(PATH_PUBLIC, 'app.py')
PATH_PID = os.path.join(PATH_WEBSRC, "wiz.pid")

@arg('--bundle', help='run as bundle')
@arg('--host', help='0.0.0.0')
@arg('--port', help='3000')
@arg('--log', help='log filename')
def run(host='0.0.0.0', port=3000, log=None, bundle=False):
    if os.path.isfile(PATH_APP) == False:
        print("Invalid Project path: wiz structure not found in this folder.")
        return

    if os.path.exists(os.path.join(PATH_WEBSRC, "project")) == False:
        os.mkdir(os.path.join(PATH_WEBSRC, "project"))

    if port is not None: 
        port = int(port)
    
    if bundle is None or bundle is False: bundle = False
    else: bundle = True

    runconfig = dict(host=host, port=port, log=log)

    def run_ctrl():
        season = importlib.import_module("season")
        app = season.server(PATH_WEBSRC)
        wiz = app.wiz()
        wiz.server.config.boot.bundle = bundle
        os.environ['WERKZEUG_RUN_MAIN'] = 'false'
        app.run(**runconfig)
        
    ostype = platform.system().lower()
    if ostype == 'linux':
        while True:
            try:
                proc = mp.Process(target=run_ctrl)
                proc.start()
                proc.join()
            except KeyboardInterrupt:
                for child in psutil.Process(proc.pid).children(recursive=True):
                    child.kill()
                return
            except:
                time.sleep(1)
                pass
    else:
        run_ctrl()

@arg('--project', help='project name')
@arg('--clean', help='project name')
def build(project="main", clean=False):
    fs = season.util.fs(os.getcwd())
    PROJECT_PATH = os.path.join("project", project)
    if fs.isdir(PROJECT_PATH) == False:
        print("project '{}' not exists".format(project))
        return
    app = season.server(os.getcwd())
    wiz = app.wiz()
    wiz.checkout.checkout(project)

    # TODO: build command

class Daemon:
    def __init__(self, pidfile, target=None, stdout='/dev/null', stderr='/dev/null'):
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.run = target
       
    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()

        so = open(self.stdout, 'w')
        se = open(self.stderr, 'w')
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        open(self.pidfile, 'w').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)
 
    def start(self):
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        self.daemonize()
        self.run(self.stdout, self.stderr)

    def stop(self):
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return

        try:
            counter = 0
            for child in psutil.Process(pid).children(recursive=True):
                counter = counter + 1
                child.kill()
            print(f"killed {counter} subprocess")
        except:
            pass

        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                sys.exit(1)

def runnable(stdout, stderr):
    def run_ctrl():
        season = importlib.import_module("season")
        app = season.server(PATH_WEBSRC)
        os.environ['WERKZEUG_RUN_MAIN'] = 'false'
        app.run()

    while True:
        try:
            proc = mp.Process(target=run_ctrl)
            proc.start()
            proc.join()
        except KeyboardInterrupt:
            for child in psutil.Process(proc.pid).children(recursive=True):
                child.kill()
            sys.exit(0)
            return
        except:
            pass
        
@arg('--force', help='force run')
@arg('--log', help='log file path')
@arg('action', default=None, help="start|stop|restart")
def server(action, force=False, log=None):
    if os.path.isfile(PATH_APP) == False:
        print("Invalid Project path: wiz structure not found in this folder.")
        return

    if log is None: log = '/dev/null'
    else: log = os.path.realpath(os.path.join(os.getcwd(), log))

    if os.path.exists(PATH_PID) and force == 'true':
        os.remove(PATH_PID)

    daemon = Daemon(PATH_PID, target=runnable, stdout=log, stderr=log)
    if action == 'start':
        print(f"WIZ server started")
        daemon.start()
    elif action == 'stop':
        print(f"WIZ server stopped")
        daemon.stop()
    elif action == 'restart':
        print("stopping WIZ server...")
        try:
            daemon.stop()
        except:
            pass
        print(f"WIZ server started")
        daemon.start()
    else:
        print(f"`wiz server` not support `{action}`. (start|stop|restart)")

def kill():
    os.system("kill -9 $(ps -ef | grep python | grep wiz | awk '{print $2}')")