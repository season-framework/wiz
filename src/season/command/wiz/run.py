import time
import os
import signal
import subprocess
import psutil
import multiprocessing as mp
import subprocess
import fnmatch

from season.command.build import PATH_PROJECT
from ... import config, core
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PATH_PROJECT = core.PATH.PROJECT

WATCH_URI = os.path.join(PATH_PROJECT, "config")

CACHE = {}

def run():
    publicpath = os.path.join(os.getcwd(), 'public')
    apppath = os.path.join(publicpath, 'app.py')
    
    if os.path.isfile(apppath) == False:
        print("Invalid Project path: season framework structure not found in this folder.")
        return

    def run_ctrl():
        cmd = "python {}".format(apppath)
        subprocess.call(cmd, shell=True)

    class Handler(FileSystemEventHandler):
        @staticmethod
        def on_any_event(event):
            try:
                if event.event_type == 'closed':
                    return
                srcpath = event.src_path[len(WATCH_URI) + 1:]
                
                CACHE['refresh'] = True
                CACHE['lasttime'] = time.time() * 1000
            except:
                pass

    mp.freeze_support()
    proc = mp.Process(target=run_ctrl)
    proc.start()

    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_URI, recursive=False)
    observer.start()

    try:
        CACHE['refresh'] = False
        CACHE['lasttime'] = time.time() * 1000

        while True:
            now = time.time() * 1000
            diff = now - CACHE['lasttime']

            if CACHE['refresh'] and diff > 500:
                pids = []
                for child in psutil.Process(proc.pid).children(recursive=True):
                    pids.append(child.pid)

                for child in psutil.Process(proc.pid).children(recursive=True):
                    try:
                        child.kill()
                    except:
                        pass

                for pid in pids:
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                    except Exception as e:
                        pass

                try:
                    proc = mp.Process(target=run_ctrl)
                    proc.start()
                except:
                    pass
                CACHE['refresh'] = False

            time.sleep(1)
    except:
        pass
    finally:
        observer.stop()
        observer.join()