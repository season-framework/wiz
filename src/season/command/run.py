from argh import arg, expects_obj
import os
import subprocess
import psutil
import season
import multiprocessing as mp

def run(*args, **kwargs):
    publicpath = os.path.join(season.path.project, 'public')
    apppath = os.path.join(publicpath, 'app.py')

    if os.path.isfile(apppath) == False:
        print("Invalid Project path: dizest structure not found in this folder.")
        return

    def run_ctrl():
        cmd = "python {}".format(apppath)
        subprocess.call(cmd, shell=True)

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