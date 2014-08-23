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
    group = parser.add_argument_group('CSS generation options')
    group.add_argument('--css-output',
                       dest='css-output', default='',
                       help='css output folder relative to' +
                            ' output-dir (default: output-dir itself)')
    group.add_argument('-C', '--css-file',
                       dest='css-file',
                       help='css file name (default: font-family with' +
                            ' .css extension)')
    group.add_argument('--css-class',
                       dest='css-class',
                       help='css class for all icons (default: composed from' +
                            ' capital letters of font-family)')
    group.add_argument('--css-prefix',
                       dest='css-prefix',
                       help='css prefix for individual icon classes' +
                            ' (default: css-class and "-")')
    group.add_argument('--css-font-url',
                       dest='css-font-url', default='url(/fonts/{fontname})',
                       help='font url template, use {fontname} placeholder' +
                            ' for font file name' +
                            ' (default: "url(/fonts/{fontname})")')
    group.add_argument('--css-aliases',
                       dest='css-aliases', default={},
                       help='css classes aliases in form' +
                            ' "icon1: alias1, alias2; icon2: other-alias1"' +
                            ' (default: no aliases)')

def parse_options(options, parser):
    options['css-output'] = os.path.join(options['output-dir'], options['css-output'])
    if options['css-file'] is None:
        options['css-file'] = options['font-family'] + '.css'
    options['css-file'] = os.path.join(options['css-output'], options['css-file'])
    if options['css-class'] is None:
        options['css-class'] = ''.join([x for x in options['font-family'] if x in string.uppercase]).lower()
    if options['css-prefix'] is None:
        options['css-prefix'] = options['css-class'] + '-'
    if options['css-aliases'] is not None:
        if isinstance(options['css-aliases'], basestring):
            d = [map(str.strip, x.split(':', 2)) for x in options['css-aliases'].split(';') if ':' in x]
            options['css-aliases'] = dict((k, map(str.strip, v.split(','))) for k, v in d)

def init(options = {}, extensions = {}, **args):
    if 'font' not in extensions:
        print 'css extension requires font extension'
        exit(1)
    options['_css'] = {}

def process(icon = None, options = {}, **args):
    options['_css'][icon['name']] = icon['code']

def finish(options = {}, **args):
    with open(options['css-file'], 'w') as css:
        css.write(COMMENTS)
        css.write('\n\n')
        css.write('@font-face {\n')
        css.write('  font-family: "{0}";\n'.format(options['font-family']))
        css.write('  src: ')

        fonts = []
        if 'woff' in options['font-formats']:
            fonts.append('{0} format(\'woff\')'.format(
                options['css-font-url'].format(
                    fontname = options['font-family'] + '.woff')))
        if 'eot' in options['font-formats']:
            fonts.append('{0} format(\'embedded-opentype\')'.format(
                options['css-font-url'].format(
                    fontname = options['font-family'] + '.eot?#iefix')))
        if 'otf' in options['font-formats']:
            fonts.append('{0} format(\'opentype\')'.format(
                options['css-font-url'].format(
                    fontname = options['font-family'] + '.otf')))
        if 'ttf' in options['font-formats']:
            fonts.append('{0} format(\'truetype\')'.format(
                options['css-font-url'].format(
                    fontname = options['font-family'] + '.ttf')))
        if 'svg' in options['font-formats']:
            fonts.append('{0} format(\'svg\')'.format(
                options['css-font-url'].format(
                    fontname = options['font-family'] + '.svg#' +
                               options['font-family'])))
        css.write(',\n       '.join(fonts) + ';\n}\n\n')

        css.write('.{0}: {{{{{1}}}}}\n\n'.format(
            options['css-class'], MAIN_CLASS
        ).format(options['font-family']))
        for icon, code in options['_css'].iteritems():
            classes = ['.{0}{1}:before'.format(options['css-prefix'], icon)]
            if icon in options['css-aliases']:
                classes += ['.{0}{1}:before'.format(options['css-prefix'], x)
                    for x in options['css-aliases'][icon]]
            css.write(', '.join(classes))
            css.write(' {{ content: "\\{:04x}"; }}\n'.format(code))
