import cairo
import rsvg
import xml.dom.minidom
import re

def process(icon = None, options = {}, **args):
    if options['debug']: print('opening SVG file {0}'.format(icon['file']))
    icon['svg'] = rsvg.Handle(file=icon['file'])

def get_dom(icon=None, file=None):
    if file is None and icon is None: return None
    if file is None: file = icon['file']
    if isinstance(file, basestring): file = open(file, 'r')
    try:
        dom = xml.dom.minidom.parse(file)
    finally:
        file.close()
    return dom

STYLES = {
    'fonts': ['font', 'font-family', 'font-size', 'font-size-adjust',
              'font-stretch', 'font-style', 'font-variant', 'font-weight'],
    'text': ['direction', 'letter-spacing', 'text-decoration', 'unicode-bidi',
             'word-spacing', 'alignment-baseline', 'baseline-shift',
             'dominant-baseline', 'glyph-orientation-horizontal',
             'glyph-orientation-vertical', 'kerning', 'text-anchor',
             'writing-mode'],
    'visual': ['clip', 'cursor', 'display', 'overflow', 'visibility',
               'clip-path', 'clip-rule', 'mask', 'opacity', 'pointer-events'],
    'filters': ['enable-background', 'filter', 'flood-color', 'flood-opacity',
                'lighting-color'],
    'gradient': ['stop-color', 'stop-opacity'],
    'colors': ['color-interpolation', 'color-interpolation-filters',
               'color-profile', 'color-rendering', 'fill', 'fill-opacity',
               'fill-rule', 'image-rendering', 'marker', 'marker-end',
               'marker-mid', 'marker-start', 'shape-rendering', 'stroke',
               'stroke-dasharray', 'stroke-dashoffset', 'stroke-linecap',
               'stroke-linejoin', 'stroke-miterlimit', 'stroke-opacity',
               'stroke-width', 'text-rendering']
}

STYLES_FLAT = [x for y in STYLES.values() for x in y]
STYLES_COLOR = ['fill', 'stroke', 'stop-color', 'flood-color', 'lighting-color']

def collect_styles(icon=None, file=None, dom=None, styles='all'):
    if icon is None and dom is None and file is None: return None
    if dom is None: dom = get_dom(icon=icon, file=file)
    result = {'_unindefinied': []}
    styles = _parse_styles_arg(styles)
    _collect_styles(dom.documentElement, result, subject=styles)
    return result

def extract_styles(icon=None, file=None, dom=None, styles=[]):
    if icon is None and dom is None and file is None: return None
    if dom is None: dom = get_dom(icon=icon, file=file)
    styles = _parse_styles_arg(styles)
    _extract_styles(dom.documentElement, subject=styles)
    return dom

def _parse_styles_arg(styles):
    if styles == 'all': return STYLES_FLAT
    if isinstance(styles, basestring): styles = [styles]
    return [x for y in styles \
               for x in (STYLES[y] if y in STYLES else [y]) \
                   if x in STYLES_FLAT]

def _collect_styles(node, styles, subject=[]):
    if node.nodeType != xml.dom.minidom.Node.ELEMENT_NODE: return None
    s = dict((k, v) for k, v in _get_styles(node) if k in subject)
    if node.hasAttribute('id'):
        styles[node.getAttribute('id')] = s
    elif s:
        styles['_unindefinied'].append(s)
    for child in node.childNodes:
        _collect_styles(child, styles, subject=subject)

def _extract_styles(node, subject=[]):
    if node.nodeType != xml.dom.minidom.Node.ELEMENT_NODE: return None
    style = [(k, v) for k, v in _get_style(node) if k not in subject]
    if len(style) > 0:
        node.setAttribute('style', ';'.join(['='.join((k, v)) for k, v in style]))
    elif node.hasAttribute('style'):
        node.removeAttribute('style')
    for attr in subject:
        if node.hasAttribute(attr):
            node.removeAttribute(attr)
    for child in node.childNodes:
        _extract_styles(child, subject=subject)

def _get_style(node):
    if not node.hasAttribute('style'): return []
    return [map(unicode.strip, x.split(':', 2))
                for x in node.getAttribute('style').split(';') if ':' in x]

def _get_styles(node):
    styles = _get_style(node)
    for attr in STYLES_FLAT:
        if node.hasAttribute(attr):
            styles.append((attr, node.getAttribute(attr)))
    styles = filter(None, map(_process_color, [(k, v) for k, v in styles if k in STYLES_FLAT]))
    return styles

COLOR_HEX_RE = re.compile('^#(\h)(\h)(\h)$', re.IGNORECASE)
COLOR_FULLHEX_RE = re.compile('^#(\h\h)(\h\h)(\h\h)$', re.IGNORECASE)
COLOR_PERCENTS_RE = re.compile('^rgb\(\s*(\d{1,3})%,(\d{1,3})%,(\d{1,3})%\s*\)$', re.IGNORECASE)
COLOR_RGB_RE = re.compile('^rgb\(\s*(\d{1,3}),(\d{1,3}),(\d{1,3})\s*\)$', re.IGNORECASE)

def _process_color(style):
    if style[0] not in STYLES_COLOR: return style
    m = COLOR_HEX_RE.match(style[1])
    if m:
        return (style[0], (
            int(m.group(1) + m.group(1), 16),
            int(m.group(2) + m.group(2), 16),
            int(m.group(3) + m.group(3), 16)
        ))
    m = COLOR_FULLHEX_RE.match(style[1])
    if m:
        return (style[0], (
            int(m.group(1), 16),
            int(m.group(2), 16),
            int(m.group(3), 16)
        ))
    m = COLOR_PERCENTS_RE.match(style[1])
    if m:
        return (style[0], (
            int(int(m.group(1)) * 2.55),
            int(int(m.group(2)) * 2.55),
            int(int(m.group(3)) * 2.55)
        ))
    m = COLOR_RGB_RE.match(style[1])
    if m:
        return (style[0], (int(m.group(1)), int(m.group(2)), int(m.group(3))))
    return False
