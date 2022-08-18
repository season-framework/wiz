import os
import sys
from argh import arg, expects_obj
import subprocess
import time
import psutil
import datetime
import platform
import signal
import atexit
import contextlib
import multiprocessing as mp

PATH_WEBSRC = os.getcwd()
PATH_PUBLIC = os.path.join(PATH_WEBSRC, 'public')
PATH_APP = os.path.join(PATH_PUBLIC, 'app.py')
PATH_PID = os.path.join(PATH_WEBSRC, "wiz.pid")

def run():
    if os.path.isfile(PATH_APP) == False:
        print("Invalid Project path: wiz structure not found in this folder.")
        return

    def run_ctrl():
        env = os.environ.copy()
        env['WERKZEUG_RUN_MAIN'] = 'true'
        cmd = str(sys.executable) + " " +  str(PATH_APP)
        subprocess.call(cmd, env=env, shell=True)

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
                pass
    else:
        run_ctrl()

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
        contextlib.redirect_stdout(so)
        contextlib.redirect_stderr(se)

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
        self.run()

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

def runnable():
    while True:
        try:
            env = os.environ.copy()
            env['WERKZEUG_RUN_MAIN'] = 'true'
            process = subprocess.Popen([str(sys.executable), str(PATH_APP)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate()
        except Exception as e:
            pass
        except:
            counter = 0
            for child in psutil.Process(os.getpid()).children(recursive=True):
                counter = counter + 1
                child.kill()
            sys.exit(0)

@arg('action', default=None, help="start|stop|restart")
def server(action):
    if os.path.isfile(PATH_APP) == False:
        print("Invalid Project path: wiz structure not found in this folder.")
        return

    daemon = Daemon(PATH_PID, target=runnable)
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
