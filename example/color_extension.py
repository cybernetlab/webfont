def process(icon=None, options={}, extensions={}, **args):
    svg = extensions['svg']
    if svg is None or icon is None: return
    dom = svg.get_dom(icon=icon)
    for x in svg.iter_styles(dom, styles='colors'):
        for k, v in x['style'].iteritems():
            if isinstance(v, svg.Color):
                print('Founded {0} style with color {1}'.format(k, v.web))