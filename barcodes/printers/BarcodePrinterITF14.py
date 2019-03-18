from .BarcodePrinter import BarcodePrinter
from .BarcodePrinter import render_bearer
from .BarcodePrinter import render_footer
from .BarcodePrinter import render_letters
from .BarcodePrinter import render_line3, render_line2
from django.template.loader import get_template

from .BarcodePrinter import TEMPLATE_DIR


class ITF14Printer(BarcodePrinter):
    """docstring for ITF13Printer"""

    def __init__(self, debug=False, scale=1, right_limit=True, font_size=12,
                 font_name='Helvetica', bar_reduction=0.00, marks=False,
                 watermark=False):
        BarcodePrinter.__init__(self, debug, scale, right_limit, font_size,
                                font_name, bar_reduction, marks, watermark)
        self.X_DIM = 1.016 #X dimension (mm)
        self.GUARDS_HEIGHT = 31.750 #guards hight
        self.SYMBOLS_HEIGHT = 32.000 #symbosl hight

        self.A_OFFSET = 6.000 #vertical offset in case of the bearer bar alone
        self.B_OFFSET = 12.000 #vertical offset in case of the bearer bar alone

        self.BEARER = 4.830 #vertical offset in case of the bearer bar alone

        self.A_OFFSET_TEXT = 45.000 #vertical offset in case of the bearer
        # bar alone
        self.B_OFFSET_TEXT = 01.500 #vertical offset in case of the bearer
        # bar alone


    def make_debug(self):
        if self.debug:
            _s = ''

            #bunch of lines (VERTICAL)

            #left bearer1 border
            _s += render_line3(x0=self.A_OFFSET - self.BEARER, y0=0, w=0,
                               h=100) # left outer

            #right bearer1 border
            _s += render_line3(x0=self.A_OFFSET, y0=0, w=0,
                               h=100) # left outer

            #10 times x dim
            _s += render_line3(x0=self.A_OFFSET + self.X_DIM * 10, y0=0, w=0,
                               h=100) # left outer
            #modules
            for i in range(121):
                _s += render_line3(
                    x0=self.A_OFFSET + self.X_DIM * 10 + i * self.X_DIM, y0=0,
                    w=0, h=100) # left outer

            # right boundary
            _s += render_line3(x0=self.A_OFFSET + self.X_DIM * 10 + 122.428,
                               y0=0, w=0, h=100) # left outer
            #
            _s += render_line3(x0=self.A_OFFSET - self.BEARER + 152.4, y0=0,
                               w=0, h=100) # right outer

            #bunch of lines (HORIZONTAL)
            _s += render_line3(x0=0, y0=self.B_OFFSET - self.BEARER - 5.84,
                               h=0.1,
                               w=400) #

            _s += render_line3(x0=0, y0=self.B_OFFSET - self.BEARER, h=0.1,
                               w=100) #

            _s += render_line3(x0=0, y0=self.B_OFFSET, h=0.1,
                               w=100) #

            _s += render_line3(x0=0, y0=self.B_OFFSET + 31.75, h=0.1,
                               w=100) #

            _s += render_line3(x0=0, y0=self.B_OFFSET + 31.75 + self.BEARER,
                               h=0.1,
                               w=100)
            return _s
        else:
            return ''

    def work(self, ean_string, data):
        cursor = self.A_OFFSET

        _s = ''

        #EPS HEADER
        #_s += self.make_header(h=140, v=438, h2=140.1, v2=438.1)
        _s += self.make_header()

        #SET FONT
        _s += self.make_font()

        #start marker
        if self.debug:
            _s += render_line2(x0=self.A_OFFSET, y0=0,
                               h=self.GUARDS_HEIGHT + 10,
                               w=0)

        #go through the barcode
        for symbol in data:
            letter, stream, number_set = symbol

            #print stream
            if self.debug:
                _s += render_line2(x0=cursor, y0=0, h=self.GUARDS_HEIGHT + 10,
                                   w=0)

            for box in self.bars(stream):
                kind, w = box #0 - light, 1 - dark
                width = 0.5 * self.X_DIM * w
                #print kind, w

                if kind == '1': #dark lines
                    bw = width - self.bar_reduction
                    _s += '%% k=%s w=%s\n' % (kind, w)
                    _s += render_line2(x0=cursor + width / 2,
                                       y0=self.B_OFFSET - 1,
                                       h=self.GUARDS_HEIGHT + 2,
                                       w=bw)

                cursor += width

        #end marker
        if self.debug:
            _s += render_line2(x0=cursor, y0=0, h=self.GUARDS_HEIGHT + 10, w=0)

        #draw a box
        _s += render_bearer(self.A_OFFSET - self.BEARER / 2,
                            self.B_OFFSET - self.BEARER / 2,
                            cursor - self.A_OFFSET + self.BEARER,
                            self.GUARDS_HEIGHT + self.BEARER,
                            self.BEARER)

        ##put text  0 50 13503 20789 5
        split_text = \
            ean_string[0] + ' ' \
            + ean_string[1:3] + ' ' \
            + ean_string[3:8] + ' ' \
            + ean_string[8:13] + ' ' \
            + ean_string[13]

        _s += render_letters(self.A_OFFSET_TEXT, self.B_OFFSET_TEXT, 0, 0,
                             split_text, 'Courier-Bold', 18)

        ##DEBUG
        _s += self.make_debug()

        #BOUNDARIES
        _s += self.make_marks()

        # watermark
        if self.watermark:
            _s += """
%--
%--watermark--
0.4 setgray
130 127 moveto
/Helvetica findfont 9  scalefont setfont
save -0.1 0 ( For preview purpose - do not reproduce!  )  ashow
save -0.1 0 (2004-2014) ashow
save /copyright glyphshow
%--
%-- /Helvetica-Bold findfont 15 scalefont setfont
%-- 1 0 0 setrgbcolor
%-- 30 35 moveto
%-- save -0.1 0 (DEMO) ashow
newpath
0 15 moveto
438 135 lineto
6 setlinewidth
1 0 0 setrgbcolor
stroke
%--
            """

        _s += render_footer()

        return _s

    def make_header(self):

        arround_offset = 10

        x0 = 1
        x1 = 438
        y0 = 0
        y1 = 140

        x0 = self.scale * x0 - arround_offset
        x1 = self.scale * x1 + arround_offset
        y0 = self.scale * y0 - arround_offset
        y1 = self.scale * y1 + arround_offset

        t = get_template(TEMPLATE_DIR % 'ps_header.html')
        ps = t.render({
            'scale': self.scale,
            'x0': int(x0),
            'x1': int(x1),
            'y0': int(y0),
            'y1': int(y1),
            'bwr': self.bar_reduction,
            'comments': ""})
        return ps
