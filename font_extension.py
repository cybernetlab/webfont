import fontforge
import cairo
import rsvg
import tempfile
import StringIO
import os
import re

FORMATS = ['otf', 'ttf', 'eot', 'woff', 'svg', 'sfd']

def get_options(parser):
    group = parser.add_argument_group('font generation options')
    group.add_argument('-l', '--font-copyright',
                       dest='font-copyright', default='OFL',
                        help='font copyright (default: "OFL")')
    group.add_argument('-n', '--font-family',
                       dest='font-family',
                       help='font family (default: camel-cased work-dir)')
    group.add_argument('-w', '--font-weight',
                       dest='font-weight', default=500, type=int,
                       help='font weight (default: 500)')
    group.add_argument('-f', '--font-formats',
                       dest='font-formats', default='all',
                       help='output font formats (default: "all")')
    group.add_argument('-F', '--font-output',
                       dest='font-output', default='',
                       help='fonts output folder (except .sfd) relative to' +
                            ' output-dir (default: output-dir itself)')
    group.add_argument('-S', '--sfd-output',
                       dest='sfd-output', default='',
                       help='SFD font output folder relative to work-dir' +
                            ' (default: work-dir itself)')

def parse_options(options, parser):
    options['font-output'] = os.path.join(options['output-dir'], options['font-output'])
    options['sfd-output'] = os.path.join(options['work-dir'], options['sfd-output'])

    if options['font-family'] is None:
        options['font-family'] = ''.join(
            x.capitalize() or '_' for x in os.path.basename(
                os.path.normpath(options['work-dir'])).split('_'))

    if options['font-formats'] == 'all': options['font-formats'] = FORMATS
    if isinstance(options['font-formats'], basestring):
        options['font-formats'] = re.split('\W+', options['font-formats'])
    for fmt in options['font-formats']:
        if fmt not in FORMATS:
            parser.error('Wrong output font format: {0}'.format(fmt))

def init(options = {}, extensions = {}, **args):
    if 'svg' not in extensions:
        print 'font extension requires svg extension'
        exit(1)
    options['_font'] = font = fontforge.font()
    font.copyright = options['font-copyright']
    font.familyname = options['font-family']
    font.fondname = options['font-family']
    font.fontname = options['font-family']
    font.fullname = options['font-family']
    font.weight = str(options['font-weight'])
    font.em = 1000

def process(icon=None, options={}, extensions={}, **args):
    if icon is None or 'svg' not in icon: return
    if options['debug']: print('processing icon {0}'.format(icon['name']))

    width = icon['svg'].props.width
    height = icon['svg'].props.height
    px2pt = 1 / 1.25
    scale = 1000 / height
    with tempfile.NamedTemporaryFile(suffix='.svg') as tmp:
        # render icon into temporary buffer
        svg = rsvg.Handle(file=icon['file'])
        buf = StringIO.StringIO()
        surface = cairo.SVGSurface(buf, scale * width * px2pt, 1000 * px2pt)
        ctx = cairo.Context(surface)
        # scale icon to have height 1000px
        ctx.scale(scale * px2pt, scale * px2pt)
        svg.render_cairo(ctx)
        surface.finish()
        buf.seek(0)
        # extract color information from icon and save it into tmp file
        dom = extensions['svg'].extract_styles(file=buf, styles=['colors'])
        tmp.write(dom.toxml().encode('utf-8'))
        tmp.seek(0)
        # import icon into font
        glyph = options['_font'].createChar(icon['code'],
                                            'uni{:04X}'.format(icon['code']))
        glyph.importOutlines(tmp.name)
        glyph.addExtrema()
        glyph.comment = icon['name']
        glyph.width = width * scale
        glyph.vwidth = height * scale

def finish(options = {}, **args):
    font = options['_font']
    font.autoHint()
    font.correctDirection()
    font.removeOverlap()
    if 'otf' in options['font-formats']:
        font.generate(os.path.join(options['font-output'], options['font-family'] + '.otf'))
    if 'woff' in options['font-formats']:
        font.generate(os.path.join(options['font-output'], options['font-family'] + '.woff'))
    if 'svg' in options['font-formats']:
        font.generate(os.path.join(options['font-output'], options['font-family'] + '.svg'))
    if 'sfd' in options['font-formats']:
        font.save(os.path.join(options['sfd-output'], options['font-family'] + '.sfd'))
    if 'ttf' in options['font-formats'] or 'eot' in options['font-formats']:
        font.em = 2048
        font.round() # ttf requires integer points
        ttf_path = os.path.join(options['font-output'], options['font-family'] + '.ttf')
        font.generate(ttf_path)
        if 'eot' in options['font-formats']:
            os.system('{0} < {1} > {2}'.format(
                os.path.join(options['root'], 'ttf2eot'),
                ttf_path,
                os.path.join(options['font-output'], options['font-family'] + '.eot')
            ))
        if 'ttf' not in options['font-formats']: os.remove(ttf_path)
    font.close()
