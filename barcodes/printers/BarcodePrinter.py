from django.template.loader import get_template

TEMPLATE_DIR = 'barcodes/ps_templates/%s'


def render_line2(x0=None, y0=None, h=None, w=None):
    line2_template = get_template(TEMPLATE_DIR % 'ps_line2.html')
    ps = line2_template.render({'x0': x0, 'y0': y0, 'h': h, 'w': w})
    return ps


def render_line3(x0=None, y0=None, h=None, w=None):
    line3_template = get_template(TEMPLATE_DIR % 'ps_line3.html')
    ps = line3_template.render({'x0': x0, 'y0': y0, 'h': h, 'w': w})
    return ps


def render_marks(box):
    marks_template = get_template(TEMPLATE_DIR % 'ps_marks.html')
    ps = marks_template.render({'box': box})
    return ps


def render_letters(x, y, ax, ay, s, font, size):
    letters_template = get_template(TEMPLATE_DIR % 'ps_letters.html')
    ps = letters_template.render(
        {'x': x, 'y': y, 'ax': ax, 'ay': ay, 's': s, 'font': font,
         'size': size})
    return ps


def render_footer():
    footer_template = get_template(TEMPLATE_DIR % 'ps_footer.html')
    ps = footer_template.render({})
    return ps


def render_right_limit(dx, dy, width):
    right_limit_template = get_template(TEMPLATE_DIR % 'ps_right_limit.html')
    ps = right_limit_template.render({'dx': dx, 'dy': dy, 'width': width})
    return ps


def render_ps_box(h):
    ps_box_template = get_template(TEMPLATE_DIR % 'ps_box.html')
    ps = ps_box_template.render(h)
    return ps


def render_bearer(x0, y0, w, h, width):
    ps_bearer_template = get_template(TEMPLATE_DIR % 'ps_bearer.html')
    ps = ps_bearer_template.render(
        {'x0': x0, 'y0': y0, 'w': w, 'h': h, 'width': width})
    return ps


class BarcodePrinter(object):
    def __init__(self, debug=False, scale=1, right_limit=True, font_size=12,
                 font_name='Helvetica', bar_reduction=0.00, marks=False,
                 watermark=False):

        self.debug = debug
        self.scale = scale
        self.right_limit = right_limit
        self.font_size = font_size
        self.font_name = font_name
        self.bar_reduction = bar_reduction
        self.dimensions = {'y1': 74, 'x1': 106, 'y0': 0, 'x0': 0}
        self.marks = marks
        self.watermark = watermark

        self.REDUCTION = {
            1: {'a': {'1': -0.025, '0': +0.025},
                'b': {'1': +0.025, '0': -0.025},
                'c': {'1': +0.025, '0': -0.025}},
            2: {'a': {'1': -0.025, '0': +0.025},
                'b': {'1': +0.025, '0': -0.025},
                'c': {'1': +0.025, '0': -0.025}},
            7: {'a': {'1': +0.025, '0': -0.025},
                'b': {'1': -0.025, '0': +0.025},
                'c': {'1': -0.025, '0': +0.025}},
            8: {'a': {'1': +0.025, '0': -0.025},
                'b': {'1': -0.025, '0': +0.025},
                'c': {'1': -0.025, '0': +0.025}}
        }

        #symbols geometry
        self.X_DIM = 0.330 #X dimension

        self.GUARDS_HEIGHT = 24.500 #guards hight
        self.SYMBOLS_HEIGHT = 22.850 #symbosl hight
        self.ADD_ON_HEIGHT = 21.300 #preis add on

        self.B_OFFSET = 1.400 # vertical offset

        #LETTERS
        self.LETTER_OFFSET_Y = 0.08 # vert offset for letters

        self.LEFT_LETTER_OFFSET_X = 0.660
        self.RIGHT_LETTER_OFFSET_X = 36

        self.PREFIX_LETTER_OFFSET_X = 5.75
        self.SUFFIX_LETTER_OFFSET_X = 20.90

        self.LETTER_X_ADD = 0.4
        self.LETTER_Y_ADD = 0

        self.RIGHT_LIMIT_OFFSET_X = 34.9
        self.RIGHT_LIMIT_OFFSET_Y = 0.1

    def bars(self, s):
        stack = []
        for c in s:
            if len(stack) == 0:
                stack.append((c, 1))
            else:
                kind, length = stack.pop()
                if kind == c:
                    stack.append((c, length + 1))
                else:
                    stack.append((kind, length))
                    stack.append((c, 1))
        return stack

    def make_header(self, comments=[]):
        arround_offset = 10
        x0 = self.scale * self.dimensions['x0'] - arround_offset
        x1 = self.scale * self.dimensions['x1'] + arround_offset
        y0 = self.scale * self.dimensions['y0'] - arround_offset
        y1 = self.scale * self.dimensions['y1'] + arround_offset
        t = get_template(TEMPLATE_DIR % 'ps_header.html')
        ps = t.render({
            'scale': self.scale,
            'x0': int(x0),
            'x1': int(x1),
            'y0': int(y0),
            'y1': int(y1),
            'bwr': self.bar_reduction,
            'comments': comments})
        return ps

    def make_font(self):
        t = get_template(TEMPLATE_DIR % 'ps_set_font.html')
        ps = t.render({'font_size': self.font_size,
                       'font_name': self.font_name})
        return ps

    def make_debug(self):
        if self.debug:
            _s = '\n% --debug--\n'
            #draw box encompasing the BC in total:
            rec = {'x1': 0, 'x2': 37.29, 'y1': 0, 'y2': 25.91}
            _s += render_ps_box(rec)
            #draw box encompasing the digits:
            rec1 = {'x1': 0, 'x2': 37.29, 'y1': 0, 'y2': 2.75}
            #rec2 = {'x1':0,'x2':37.29,'y1':2.75, 'y2':2.75 + 0.33}
            _s += render_ps_box(rec1)
            #_s += render_ps_box(rec2)

            #draw 113  lines showing modules
            for i in range(113):
                _s += render_line3(x0=self.X_DIM * i + self.X_DIM / 2, y0=0,
                                   h=15, w=0.01)

            return _s
        else:
            return ''

    def make_marks(self):
        if self.marks:
            _s = '\n% --marks--\n'
            rec = {'x1': 0, 'x2': 37.29, 'y1': 0, 'y2': 25.91}
            _s += render_marks(rec)
            return _s
        else:
            return ''
