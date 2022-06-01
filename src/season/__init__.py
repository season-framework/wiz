import os

from season import util
from season.core import exception
from season.core.lib.instances.wiz import wiz
from season.core.lib.instances.plugin import plugin
from season.core.server import Server
from season.core.bootstrap import bootstrap

stdClass = util.std.stdClass

path = stdClass()
path.lib =  os.path.dirname(__file__)
path.project =  os.path.join(os.getcwd())
path.websrc = os.path.join(path.project, 'websrc')
path.public = os.path.join(path.project, 'public')
path.config = os.path.join(path.project, 'config')

log = stdClass()
log.debug = 0
log.info = 1
log.dev = 2
log.warning = 3
log.error = 4
log.critical = 5

cache = stdClass()