import argparse
import os
import yaml
import re

FORMATS = ['otf', 'ttf', 'eot', 'woff', 'svg', 'sfd']

def parse():
	arg_parser = argparse.ArgumentParser(description='Make webfont from SVG icons.')
	arg_parser.add_argument('-c', '--config', dest='config',
	                   		help='config file location (default: search for ' +
	                   			 '.webfont.yml in current folder and user home)')
	arg_parser.add_argument('-d', '--work-dir', dest='work-dir', default='',
	                   		help='project root path (default: config directory)')
	arg_parser.add_argument('-o', '--output-dir', dest='output-dir', default='',
	                   		help='output folder relative to work-dir (default: work-dir itself)')
	arg_parser.add_argument('-i', '--icons-dir', dest='icons-dir', default='icons',
	                   		help='icons path relative to work-dir (default: icons)')
	arg_parser.add_argument('-D', '--debug', dest='debug', default=False, action='store_true',
	                   		help='print some debug info (default: False)')
	arg_parser.add_argument('-l', '--font-copyright', dest='font-copyright', default='OFL',
	                   		help='font copyright (default: "OFL")')
	arg_parser.add_argument('-n', '--font-family', dest='font-family',
	                   		help='font family (default: camel-cased work-dir)')
	arg_parser.add_argument('-w', '--font-weight', dest='font-weight', default=500, type=int,
	                   		help='font weight (default: 500)')
	arg_parser.add_argument('-f', '--font-formats', dest='font-formats', default='all',
	                   		help='output font formats (default: "all")')
	arg_parser.add_argument('-F', '--font-output', dest='font-output', default='',
	                   		help='fonts output folder (except .sfd) relative to output-dir (default: output-dir itself)')
	arg_parser.add_argument('-S', '--sfd-output', dest='sfd-output', default='',
	                   		help='SFD font output folder relative to work-dir (default: work-dir itself)')
	
	options = vars(arg_parser.parse_args())
	
	if options['config'] is None:
		options['config'] = os.path.join(os.getcwd(), '.webfont.yml')
		if not os.path.isfile(options['config']):
			options['config'] = os.path.join(os.path.expanduser('~'), '.webfont.yml')
	if not os.path.isfile(options['config']): options['config'] = None
	
	if options['config'] is not None:
		stream = open(options['config'], 'r')
		try:
			config = yaml.load(stream)
		finally:
			stream.close()
		if 'config' in config:
			if config['config'] is None: config['config'] = {}
			options = dict(options.items() + config['config'].items())
	
	config_dir = os.path.dirname(options['config']) if options['config'] is not None else os.path.expanduser('~')

	options['work-dir'] = os.path.join(config_dir, options['work-dir'])
	options['icons-dir'] = os.path.join(options['work-dir'], options['icons-dir'])
	options['output-dir'] = os.path.join(options['work-dir'], options['output-dir'])
	options['font-output'] = os.path.join(options['output-dir'], options['font-output'])
	options['sfd-output'] = os.path.join(options['work-dir'], options['sfd-output'])

	if not os.path.isdir(options['work-dir']):
		print 'Working directory {0} doen\'t exists'.format(options['work-dir'])
		exit(1)
	if not os.path.isdir(options['icons-dir']):
		print 'Icons directory {0} doen\'t exists'.format(options['icons-dir'])
		exit(1)

	if options['font-family'] is None:
		options['font-family'] = ''.join(
			x.capitalize() or '_' for x in os.path.basename(os.path.normpath(options['work-dir'])).split('_')
		)

	if options['font-formats'] == 'all': options['font-formats'] = FORMATS
	if isinstance(options['font-formats'], basestring):
		options['font-formats'] = re.split('\W+', options['font-formats'])
	for fmt in options['font-formats']:
		if fmt not in FORMATS:
			print('Wrong output font format: {0}'.format(fmt))
			exit(1)
	
	return options