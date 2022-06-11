import os

from season import util
from season.core import exception
from season.core.lib.instances.wiz import wiz
from season.core.lib.instances.plugin import plugin
from season.core.server import Server
from season import cmd

from .version import VERSION_STRING as VERSION
version = __version__ = __VERSION__ = VERSION

stdClass = util.std.stdClass

path = stdClass()
path.lib =  os.path.dirname(__file__)
path.project =  os.path.join(os.getcwd())
path.websrc = os.path.join(path.project, 'websrc')
path.public = os.path.join(path.project, 'public')
path.config = os.path.join(path.project, 'config')

log = stdClass()
log.debug = 0      # response info
log.info = 1       # server process messages
log.warning = 2    # http error
log.dev = 3        # user log
log.error = 4      # code error
log.critical = 5   # uncatched error

cache = stdClass()