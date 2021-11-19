import time
import os
import subprocess
import psutil
import multiprocessing as mp
import subprocess
import fnmatch

from season.command.build import PATH_PROJECT
from .. import config, core
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PATH_PROJECT = core.PATH.PROJECT

seasonconfig = config.load().data
PATTERNS = []
try:
    if type(seasonconfig['watch']['pattern']) == str:
        PATTERNS = seasonconfig['watch']['pattern'].split(",")
    elif type(seasonconfig['watch']['pattern']) == list:
        PATTERNS = seasonconfig['watch']['pattern']
    else:
        PATTERNS = ["*"]    
except:
    PATTERNS = ["*"]

IGNORES = []
try:
    if type(seasonconfig['watch']['ignore']) == str:
        IGNORES = seasonconfig['watch']['ignore'].split(",")
    elif type(seasonconfig['watch']['ignore']) == list:
        IGNORES = seasonconfig['watch']['ignore']
except:
    pass
IGNORES.append("websrc")

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
                srcpath = event.src_path[len(PATH_PROJECT) + 1:]
                for pt in IGNORES:
                    if fnmatch.fnmatch(srcpath, pt):
                        return

                matched = False
                for pt in PATTERNS:
                    matched = fnmatch.fnmatch(srcpath, pt)
                    if matched:
                        break

                if matched:
                    CACHE['refresh'] = True
                    CACHE['lasttime'] = time.time() * 1000
            except:
                pass

    mp.freeze_support()
    proc = mp.Process(target=run_ctrl)
    proc.start()

    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, os.path.join(os.getcwd(), 'websrc'), recursive=True)
    observer.start()

    try:
        CACHE['refresh'] = False
        CACHE['lasttime'] = time.time() * 1000

        while True:
            now = time.time() * 1000
            diff = now - CACHE['lasttime']
            if CACHE['refresh'] and diff > 500:
                try:
                    for child in psutil.Process(proc.pid).children(recursive=True):
                        child.kill()
                except:
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