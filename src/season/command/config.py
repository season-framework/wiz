import os
import json
from argh import arg, expects_obj

PATH_FRAMEWORK = os.path.dirname(os.path.dirname(__file__))
PATH_PROJECT = os.path.join(os.getcwd())
PATH_PUBLIC = os.path.join(PATH_PROJECT, 'public')
PATH_WEBSRC = os.path.join(PATH_PROJECT, 'websrc')
PATH_MODULE = os.path.join(PATH_WEBSRC, 'modules')
PATH_TMP = os.path.join(PATH_PROJECT, '.tmp')
PATH_CONFIG = os.path.join(PATH_PROJECT, 'sf.json')

# additional functions
def write_file(path, content):
    f = open(path, mode="w")
    f.write(content)
    f.close()

# default.module: module
@arg('--set', default=None, help='key')
@arg('--unset', default=None, help='key')
@arg('--value', default=None, help='value')
@expects_obj
def config(args):
    if os.path.isdir(PATH_PUBLIC) == False or os.path.isdir(PATH_WEBSRC) == False:
        print("invalid project path: season framework structure not found in this folder.")
        return

    if os.path.isfile(PATH_CONFIG) == False:
        write_file(PATH_CONFIG, '{}')

    f = open(PATH_CONFIG)
    config = json.load(f)
    f.close()

    if args.set is not None:
        config[args.set] = args.value

    if args.unset is not None:
        del config[args.unset]

    write_file(PATH_CONFIG, json.dumps(config, sort_keys=True, indent=4))