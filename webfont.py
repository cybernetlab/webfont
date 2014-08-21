#!/usr/bin/python

import sys
import os
import glob
import re
import importlib
import argparse
import yaml

ICON_RE = re.compile('^uni([0-9a-fA-F]+)_([a-zA-Z][a-zA-Z0-9\-]*)' +
                     '(?:_([a-zA-Z\-]+))?\.svg$')
BUILTIN = set(['svg', 'font'])

# icons generator
def get_icons(folder):
    for svg_file in glob.iglob(os.path.join(folder, 'uni*.svg')):
        m = ICON_RE.match(svg_file.split('/')[-1])
        if m is None: continue
        icon = {
            'file': svg_file,
            'code': int(m.group(1), base=16),
            'name': m.group(2),
            'extensions': BUILTIN
        }
        if m.group(3) is not None:
            icon['extensions'] |= set(m.group(3).split('-'))
        yield icon


# main options
arg_parser = argparse.ArgumentParser(description='Make webfont from SVG icons.',
                                     add_help=False)
arg_parser.add_argument('-c', '--config',
                        dest='config',
                        help='config file location (default: search for' +
                             ' .webfont.yml in current folder and user home)')
arg_parser.add_argument('-d', '--work-dir',
                        dest='work-dir', default='',
                        help='project root path (default: config directory)')
arg_parser.add_argument('-o', '--output-dir',
                        dest='output-dir', default='',
                        help='output folder relative to work-dir' +
                             ' (default: work-dir itself)')
arg_parser.add_argument('-i', '--icons-dir',
                        dest='icons-dir', default='icons',
                           help='icons path relative to work-dir (default: icons)')
arg_parser.add_argument('-D', '--debug',
                        dest='debug', default=False, action='store_true',
                        help='print some debug info (default: False)')

# parse main options and save unknown options for parsing in modules
options, module_args = arg_parser.parse_known_args()
options = vars(options)

if options['config'] is None:
    options['config'] = os.path.join(os.getcwd(), '.webfont.yml')
    if not os.path.isfile(options['config']):
        options['config'] = os.path.join(os.path.expanduser('~'), '.webfont.yml')

if not os.path.isfile(options['config']): options['config'] = None

# load config file
if options['config'] is not None:
    stream = open(options['config'], 'r')
    try:
        config = yaml.load(stream)
    except yaml.scanner.ScannerError as e:
        print('Invalid config file: {0}'.format(e))
        stream.close()
        exit(1)
    finally:
        stream.close()
    if 'config' in config:
        if config['config'] is None: config['config'] = {}
        options = dict(options.items() + config['config'].items())

# basic options parsing
config_dir = os.path.dirname(options['config']) \
    if options['config'] is not None else os.path.expanduser('~')
options['work-dir'] = os.path.join(config_dir, options['work-dir'])
options['icons-dir'] = os.path.join(options['work-dir'], options['icons-dir'])
if not os.path.isdir(options['work-dir']):
    parser.error('Working directory {0} doen\'t exists'.format(options['work-dir']))
if not os.path.isdir(options['icons-dir']):
    parser.error('Icons directory {0} doen\'t exists'.format(options['icons-dir']))

# add modules extensions folders
options['root'] = os.path.abspath(os.path.dirname(__file__))
ext_dir = os.path.join(options['work-dir'], 'extensions')
if os.path.isdir(ext_dir): sys.path += [ext_dir]

try:
    icons = list(get_icons(options['icons-dir']))

    # retrieve module list
    modules = dict(
        (ext, importlib.import_module('extensions.' + ext)) \
            for ext in reduce(lambda a, x: a | x['extensions'], icons, set())
    )

    # get modules options
    for module in modules.values():
        if hasattr(module, 'get_options'):
            module.get_options(arg_parser)

    # parse unknown options for modules
    options = dict(vars(arg_parser.parse_args(module_args)).items() +
                   options.items())

    # module-specific options parsing
    for module in modules.values():
        if hasattr(module, 'parse_options'):
            module.parse_options(options, arg_parser)

    if options['debug']: print('options are: {0}'.format(options))

    # initialize modules
    for module in modules.values():
        if hasattr(module, 'init'):
            module.init(options=options, icons=icons)

    # iterate through icons
    for icon in icons:
        for ext in icon['extensions']:
            modules[ext].process(options=options, icon=icon)

    # modules teardown
    for module in modules.values():
        if hasattr(module, 'finish'):
            module.finish(options=options, icons=icons)

finally:
    None
