import os
import string

COMMENTS = """/*
  This file is created automatically by webfont.py font generator
  WARNING! Don't change this file. Make changes in webfont config file instead
*/"""

MAIN_CLASS = """
  display: inline-block;
  font-family: "{0}";
  font-style: normal;
  font-weight: normal;
  line-height: 1;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
"""

def get_options(parser):
    group = parser.add_argument_group('CSS variables generation options')
    group.add_argument('--css-vars-output',
                       dest='css-vars-output', default='',
                       help='css variables output folder relative to' +
                            ' output-dir (default: output-dir itself)')
    group.add_argument('-V', '--css-vars-file',
                       dest='css-vars-file',
                       help='css file name (default: {font-family}_vars.css')
    group.add_argument('--css-vars-prefix',
                       dest='css-vars-prefix',
                       help='css variables prefix for individual icon classes' +
                            ' (default: "icon-")')
    group.add_argument('--css-vars-properties',
                       dest='css-vars-properties',
                       default=['color'],
                       help='space separated list of icon properties for' +
                            ' which you want to create variables. Only' +
                            ' "color" is now supported (default: "color")')

def parse_options(options, parser):
    options['css-vars-output'] = os.path.join(options['output-dir'], options['css-vars-output'])
    if options['css-vars-file'] is None:
        options['css-vars-file'] = options['font-family'] + '_vars.css'
    options['css-vars-file'] = os.path.join(options['css-vars-output'], options['css-vars-file'])
    if options['css-vars-prefix'] is None:
        options['css-vars-prefix'] = 'icon-'
    if options['css-vars-properties'] is not None:
        if isinstance(options['css-vars-properties'], basestring):
            options['css-vars-properties'] = options['css-vars-properties'].split
    else:
        options['css-vars-properties'] = ['class']

def init(options = {}, extensions = {}, **args):
    if 'css' not in extensions or 'svg' not in extensions:
        print 'css vars extension requires css and svg extension'
        exit(1)
    options['_css_vars'] = {}

def set(icon, prop, value):
    if icon is None: return
    icon['options']['_css_vars']['{0}{1}-{2}'.format(
        icon['options']['css-vars-prefix'],
        icon['name'],
        prop
    )] = value

def process(icon = None, extensions = {}, **args):
    for x in extensions['css'].get_names(icon = icon):
        for prop in icon['options']['css-vars-properties']:
            value = None
            if prop == 'color':
                color = extensions['svg'].get_color(icon = icon)
                if color is not None: value = color.web
            set(icon, prop, value)

def finish(options = {}, **args):
    with open(options['css-vars-file'], 'w') as css:
        css.write(COMMENTS)
        css.write('\n\n')
        for k, v in options['_css_vars'].iteritems():
            if v is None: continue
            css.write('${0}: {1};\n'.format(k, v))
