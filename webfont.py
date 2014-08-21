#!/usr/bin/python

import sys
import os
import glob
import re
import importlib

import webfont_options
import webfont_svg

ICON_RE = re.compile('^uni([0-9a-fA-F]+)_([a-zA-Z][a-zA-Z0-9\-]*)' +
					 '(_[a-zA-Z\-]+)?\.svg$')
BUILTIN = set(['svg', 'font'])

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
		if m.group(3) is not None: icon['extensions'] |= set(m.group(3).split('-'))
		yield icon

options = webfont_options.parse()
options['root'] = os.path.dirname(__file__)
ext_dir = os.path.join(options['work-dir'], 'extensions')
if os.path.isdir(ext_dir): sys.path += [ext_dir]

try:
	icons = list(get_icons(options['icons-dir']))

	modules = dict(
		(ext, importlib.import_module('extensions.' + ext))
			for ext in reduce(lambda a, x: a | x['extensions'], icons, set())
	)

	for module in modules.values():
		if hasattr(module, 'init'): module.init(options=options, icons=icons)

	for icon in icons:
		for ext in icon['extensions']:
			modules[ext].process(options=options, icon=icon)

	for module in modules.values():
		if hasattr(module, 'finish'): module.finish(options=options, icons=icons)

finally:
	None
