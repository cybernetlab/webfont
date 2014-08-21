import cairo
import rsvg

def process(icon, options):
    if options['debug']: print('opening SVG file {0}'.format(icon['file']))
    icon['svg'] = rsvg.Handle(file=icon['file'])
