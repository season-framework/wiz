import season
import platform
import socket

def status():
    res = dict()
    res['hostname'] = socket.gethostname()
    res['project'] = wiz.project()
    res['wiz'] = season.version
    res['python'] = platform.python_version()
    wiz.response.status(200, res)