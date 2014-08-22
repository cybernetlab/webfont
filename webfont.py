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

# icons generator
def get_icons(options):
    folder = options['icons-dir']
    for svg_file in glob.iglob(os.path.join(folder, 'uni*.svg')):
        m = ICON_RE.match(svg_file.split('/')[-1])
        if m is None: continue
        icon = {
            'file': svg_file,
            'code': int(m.group(1), base=16),
            'name': m.group(2),
            'extensions': set(options['default-extensions'])
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
arg_parser.add_argument('-e', '--default-extensions',
                        dest='default-extensions', default='svg font css',
                        help='comma separated default extensions' +
                             ' (default: "svg font css")')

# parse main options and save unknown options for parsing in extensions
options, extensions_args = arg_parser.parse_known_args()
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
options['output-dir'] = os.path.join(options['work-dir'], options['output-dir'])
options['icons-dir'] = os.path.join(options['work-dir'], options['icons-dir'])
if not os.path.isdir(options['work-dir']):
    parser.error('Working directory {0} doen\'t exists'.format(options['work-dir']))
if not os.path.isdir(options['icons-dir']):
    parser.error('Icons directory {0} doen\'t exists'.format(options['icons-dir']))
if isinstance(options['default-extensions'], basestring):
    options['default-extensions'] = re.split('\W+', options['default-extensions'])

# add user extensions folders
if options['debug']: print('Loading extensions. Options are: {0}'.format(options))
options['root'] = os.path.abspath(os.path.dirname(__file__))
if options['work-dir'] not in sys.path:
    sys.path.insert(0, options['work-dir'])

try:
    icons = list(get_icons(options))

    # import extension list
    extensions = dict(
        (ext, importlib.import_module(ext + '_extension')) \
            for ext in reduce(lambda a, x: a | x['extensions'], icons, set())
    )

    # get extensions options
    for ext in extensions.values():
        if hasattr(ext, 'get_options'):
            ext.get_options(arg_parser)

    # parse unknown options for extensions
    options = dict(vars(arg_parser.parse_args(extensions_args)).items() +
                   options.items())

    # ext-specific options parsing
    for ext in extensions.values():
        if hasattr(ext, 'parse_options'):
            ext.parse_options(options, arg_parser)

    if options['debug']: print('Extensions loaded. Options are: {0}'.format(options))

    # initialize extensions
    for ext in extensions.values():
        if hasattr(ext, 'init'):
            ext.init(options=options,
                     icons=icons,
                     extensions=extensions)

    # iterate through icons
    for icon in icons:
        for ext in icon['extensions']:
            extensions[ext].process(options=options,
                                    icon=icon,
                                    extensions=extensions)

    # extensions teardown
    for ext in extensions.values():
        if hasattr(ext, 'finish'):
            ext.finish(options=options,
                       icons=icons,
                       extensions=extensions)

finally:
    None
