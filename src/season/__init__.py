import os

from season import util
from season import core

from season.lib.server import Server as app
from season.lib.plugin import Plugin as plugin

from .version import VERSION_STRING as VERSION
version = __version__ = __VERSION__ = VERSION

LOG_DEBUG = 0
LOG_INFO = 1
LOG_WARNING = 2
LOG_DEV = 3
LOG_ERROR = 4
LOG_CRIT = LOG_CRITICAL = 5

PATH_LIB = os.path.dirname(__file__)
