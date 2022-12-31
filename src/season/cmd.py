import sys
import os
import argh
ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.realpath(os.path.join(ROOT_PATH, '..')))
__package__ = "season"

from .version import VERSION_STRING
from .command.run import run, server, kill
from .command.create import create
from .command.plugin import plugin
from .command.ide import ide

def main():
    epilog = "Copyright 2021 SEASON CO. LTD. <proin@season.co.kr>. Licensed under the terms of the MIT license. Please see LICENSE in the source code for more information."
    parser = argh.ArghParser(epilog=epilog)
    parser.add_commands([
        run, server, kill, create, plugin, ide
    ])
    parser.add_argument('--version', action='version', version='season ' + VERSION_STRING)
    parser.dispatch()

if __name__ == '__main__':
    main()