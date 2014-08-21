import fontforge
import cairo
import rsvg
import tempfile
import os
import re

FORMATS = ['otf', 'ttf', 'eot', 'woff', 'svg', 'sfd']

# used to disable output from fontforge
#class NullWriter(object):
#	def write(self, arg): pass
#
#def disable_output(options):
#	if options['debug']: return
#	options['_stdout'] = sys.stdout
#	#sys.stdout = NullWriter()
#
#def enable_output(options):
#	if options['debug']: return
#	sys.stdout = options['_stdout']

def get_options(parser):
	group = parser.add_argument_group('font creation options')
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
	options['output-dir'] = os.path.join(options['work-dir'], options['output-dir'])
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

def init(options = {}, **args):
	options['_font'] = font = fontforge.font()
	font.copyright = options['font-copyright']
	font.familyname = options['font-family']
	font.fondname = options['font-family']
	font.fontname = options['font-family']
	font.fullname = options['font-family']
	font.weight = str(options['font-weight'])
	font.em = 1000

def process(icon = None, options = {}, **args):
	if icon is None: return
	if options['debug']: print('processing icon {0}'.format(icon['name']))

	width = icon['svg'].props.width
	height = icon['svg'].props.height
	if height != 1000:
		scale = 1000 / height
		tmp = tempfile.NamedTemporaryFile(suffix='.svg', delete=False)
		surface = cairo.SVGSurface(tmp, scale * width / 1.25, 1000 / 1.25)
		ctx = cairo.Context(surface)
		ctx.scale(scale / 1.25, scale / 1.25)
		icon['svg'].render_cairo(ctx)
		surface.finish()
		tmp.close()
		svg = tmp.name
		width = width * scale
		height = height * scale
	else:
		svg = icon['file']
	glyph = options['_font'].createChar(icon['code'], 'uni{:04X}'.format(icon['code']))
	try:
		#disable_output(options)
		glyph.importOutlines(svg)
		#enable_output(options)
		glyph.addExtrema()
	except:
		print('Error importing icon "{0}" - invalid SVG'.format(icon['name']))
		return
	glyph.comment = icon['name']
	glyph.width = width
	glyph.vwidth = height

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
