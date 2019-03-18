from .BarcodePrinter import BarcodePrinter
from .BarcodePrinter import render_footer
from .BarcodePrinter import render_letters
from .BarcodePrinter import render_line2
from .BarcodePrinter import render_right_limit


class EAN13Printer(BarcodePrinter):
    """docstring for BarcodePrinter"""

    def __init__(self,
                 debug=False, scale=1, right_limit=True, font_size=12,
                 font_name='Helvetica', bar_reduction=0.00, marks=False,
                 watermark=False):

        BarcodePrinter.__init__(self, debug, scale, right_limit, font_size,
                                font_name, bar_reduction, marks, watermark)


    def work(self, ean_string, data):

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

            #DIGITS
            #_s += self.make_letter(cursor + 1.15,letter)

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
                                        letter == 1 or letter == 2 or letter
                                == 7
                        or letter == 8):
                        reduction = self.REDUCTION[letter][number_set][kind]

                        #box = {'x1':cursor-reduction/2 ,
                        # 'x2':cursor+width+reduction/2,
                        #box = {'x1':cursor,'x2':cursor+width,
                        #'y1':self.B_OFFSET+5*self.X_DIM, 'y2':self
                        # .SYMBOLS_HEIGHT+self.B_OFFSET+5*self.X_DIM}
                        bw = width - self.bar_reduction
                        _s += render_line2(x0=cursor + width / 2,
                                           y0=self.B_OFFSET + 5 * self.X_DIM,
                                           h=self.SYMBOLS_HEIGHT,
                                           w=bw + reduction)

                    else:
                        #box = {'x1':cursor,'x2':cursor+width,
                        #'y1':self.B_OFFSET+5*self.X_DIM, 'y2':self
                        # .SYMBOLS_HEIGHT+self.B_OFFSET+5*self.X_DIM}
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
1 75 moveto
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
