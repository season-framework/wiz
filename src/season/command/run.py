import sys
from argh import arg, expects_obj
import os
import subprocess
import psutil
import season
import multiprocessing as mp
import platform

def run():
    publicpath = os.path.join(season.path.project, 'public')
    apppath = os.path.join(publicpath, 'app.py')
    if os.path.isfile(apppath) == False:
        print("Invalid Project path: wiz structure not found in this folder.")
        return

    def run_ctrl():
        env = os.environ.copy()
        env['WERKZEUG_RUN_MAIN'] = 'true'
        cmd = str(sys.executable) + " " +  str(apppath)
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