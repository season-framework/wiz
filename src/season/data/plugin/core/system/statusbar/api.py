import season
import platform
import socket

def status():
    res = dict()
    res['hostname'] = socket.gethostname()
    res['branch'] = wiz.branch()
    res['wiz'] = season.version
    res['python'] = platform.python_version()
    wiz.response.status(200, res)