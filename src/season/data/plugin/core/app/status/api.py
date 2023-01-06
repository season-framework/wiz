import os
import time
import psutil
import platform
import resource
import signal
import season

def status():
    process = psutil.Process(os.getpid())
    hdd = psutil.disk_usage('/')

    stat = season.util.std.stdClass()
    stat.system_pid = os.getpid()
    stat.system_uptime = int(time.time() - psutil.boot_time())

    stat.wiz_version = season.version
    stat.python_version = platform.python_version()

    stat.memory_usage = psutil.virtual_memory().used
    stat.memory_wiz_usage = process.memory_info().rss
    stat.memory_total = psutil.virtual_memory().total

    stat.cpu_count = psutil.cpu_count()
    stat.cpu_usage = psutil.cpu_percent()
    stat.cpu_wiz_usage = process.cpu_percent()

    stat.disk_total = hdd.total
    stat.disk_used = hdd.used
    stat.disk_free = hdd.free

    children = process.children(recursive=True)
    processes = []
    for child in children:
        obj = dict()
        obj['status'] = child.status()
        obj['pid'] = child.pid
        obj['parent'] = child.parent().pid
        obj['cmd'] = child.name()
        obj['time'] = int(time.time() - child.create_time())
        processes.append(obj)
    stat.process_count = len(processes)
    stat.process_children = processes

    wiz.response.status(200, stat)

def restart():
    pid = os.getpid()
    for child in psutil.Process(pid).children(recursive=True):
        child.terminate()
        os.kill(child.pid, signal.SIGKILL)
    os.kill(pid, signal.SIGKILL)
    wiz.response.status(200)