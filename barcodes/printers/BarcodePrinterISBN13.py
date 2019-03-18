from .BarcodePrinterEAN13 import EAN13Printer
from .BarcodePrinter import render_line2
from .BarcodePrinter import render_letters
from .BarcodePrinter import render_footer
from .BarcodePrinter import render_right_limit
from .BarcodePrinter import render_marks


class ISBN13Printer(EAN13Printer):
    """docstring for BarcodePrinter"""

    def __init__(self, debug=False, scale=1, right_limit=True, font_size=12,
                 font_name='Helvetica', bar_reduction=0.00, marks=False,
                 watermark=False):

        EAN13Printer.__init__(self, debug, scale, right_limit, font_size,
                              font_name, bar_reduction, marks, watermark)

        self.dimensions = {'y1': 84, 'x1': 106, 'y0': 0, 'x0': 0}

        self.UPPER_BOUNDARY = 29.5


    def work(self, ean_string, data):

        ean_string, isbn = ean_string.split(':')

        cursor = 0.00

        _s = ''

        #EPS HEADER
        _s += self.make_header()

        #DEBUG
        _s += self.make_debug()

        #BOUNDARIES
        _s += self.make_marks()

        #SET FONT
        _s += self.make_font()

        #GO THROUGH WHAT WE'VE GOT AS SYMBOL
        for symbol in data:
            letter, stream, number_set = symbol
            #BARS
            for box in self.bars(stream):
                kind, w = box #0 - light, 1 - dark
                width = self.X_DIM * w
                #GUARD BARS
                if letter == 'g' and kind == '1': #guards
                    bw = width - self.bar_reduction
                    _s += render_line2(x0=cursor + width / 2, y0=self.B_OFFSET,
                                       h=self.GUARDS_HEIGHT, w=bw)
                    #SYMBOL BARS
                if str(letter).isdigit() and kind == '1':
                    if (
                                    letter == 1 or letter == 2 or letter == 7
                        or letter == 8):
                        reduction = self.REDUCTION[letter][number_set][kind]
                        bw = width - self.bar_reduction
                        _s += render_line2(x0=cursor + width / 2,
                                           y0=self.B_OFFSET + 5 * self.X_DIM,
                                           h=self.SYMBOLS_HEIGHT,
                                           w=bw + reduction)
                    else:
                        bw = width - self.bar_reduction
                        _s += render_line2(x0=cursor + width / 2,
                                           y0=self.B_OFFSET + 5 * self.X_DIM,
                                           h=self.SYMBOLS_HEIGHT, w=bw)
                cursor += width
        #print first LETTER
        _s += render_letters(self.LEFT_LETTER_OFFSET_X,
                             self.LETTER_OFFSET_Y,
                             0,
                             0,
                             str(ean_string[0]),
                             self.font_name,
                             self.font_size)
        #print first 6 digits
        _s += render_letters(self.PREFIX_LETTER_OFFSET_X,
                             self.LETTER_OFFSET_Y,
                             self.LETTER_X_ADD,
                             self.LETTER_Y_ADD,
                             str(ean_string[1:7]),
                             self.font_name,
                             self.font_size)
        #print last 6 digits
        _s += render_letters(self.SUFFIX_LETTER_OFFSET_X,
                             self.LETTER_OFFSET_Y,
                             self.LETTER_X_ADD,
                             self.LETTER_Y_ADD,
                             str(ean_string[7:]),
                             self.font_name,
                             self.font_size)

        #calculate the distance between letters
        if len(isbn) == 22:
            isbn_start = -0.1
            isbn_letter_distance = -0.2
        else:
            isbn_start = 2.3
            isbn_letter_distance = 0.0

        # ISBN Text
        _s += render_letters(isbn_start,
                             27.5,
                             isbn_letter_distance,
                             self.LETTER_Y_ADD,
                             isbn,
                             'Courier',
                             9)

        #print last LETTER
        if self.right_limit:
            _s += render_right_limit(self.RIGHT_LIMIT_OFFSET_X,
                                     self.RIGHT_LIMIT_OFFSET_Y, 0.75)
        # watermark
        if self.watermark:
            _s += """
%--
%--watermark--
0.4 setgray
1 85 moveto
/Helvetica findfont 5  scalefont setfont
save -0.1 0 ( For preview purpose - do not reproduce!  )  ashow
save -0.1 0 (2004-2014 ) ashow
save /copyright glyphshow
%--
%-- /Helvetica-Bold findfont 15 scalefont setfont
%-- 1 0 0 setrgbcolor
%-- 30 35 moveto
%-- save -0.1 0 (DEMO) ashow
newpath
0 15 moveto
105 60 lineto
3 setlinewidth
1 0 0 setrgbcolor
stroke
%--
            """

        #FOOTER
        _s += render_footer()
        return _s


# def make_debug(self):
    #     if self.debug:
    #         _s = ''
    #         #draw box encompasing the BC in total - main smbol:
    #         rec = {'x1':0,'x2':37.29,'y1':0, 'y2':self.UPPER_BOUNDARY}
    #         _s += render.rect(storage(rec))
    #         #draw box encompasing the digits:
    #         rec1 = {'x1':0,'x2':37.29,'y1':0,    'y2':2.75}
    #         rec2 = {'x1':0,'x2':37.29,'y1':2.75, 'y2':2.75 + 0.33}
    #         _s += render.rect(storage(rec1))
    #         _s += render.rect(storage(rec2))
    #         #draw 113  lines showing modules
    #         for i in range(165):
    #             _s += render.line(x0=self.X_DIM*i+self.X_DIM/2,y0=0,x1=0,
    # y1=10)
    #         return _s
    #     else:
    #         return ''

#def make_marks(self):
#    if self.marks:
#        _s = ''
#        rec = {'x1': 0, 'x2': 37.29, 'y1': 0, 'y2': self.UPPER_BOUNDARY}
#        _s += render_marks(rec)
#        return _s
#    else:
#        return ''
