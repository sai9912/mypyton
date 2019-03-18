# class RSS14Printer(BarcodePrinter):
#     """docstring for RSS14Printer"""

#     def __init__(self,debug=False,scale=1,right_limit=True,font_size=12,font_name='Helvetica',bar_reduction=0.00,marks=False):
#         BarcodePrinter.__init__(self,debug,scale,right_limit,font_size,font_name,bar_reduction,marks)

#         #self.X_DIM = 0.25 #X dimension
#         self.X_DIM = 0.33 #X dimension

#         self.font_size = 7

#         self.A_OFFSET = 3
#         self.B_OFFSET = 8

#         self.LEFT_LETTER_OFFSET_X = 3.5
#         self.LETTER_OFFSET_Y = 7

#     def work(self,(ean_string,data)):

#         cursor = self.A_OFFSET
#         _s = ''

#         #EPS HEADER
#         _s += self.make_header()

#         #SET FONT
#         _s += self.make_font()

#         #GO THROUGH WHAT WE'VE GOT AS SYMBOL
#         for symbol in data:
#             letter, stream, number_set = symbol


#             #BARS
#             for box in self.bars(stream):
#                 kind, w = box #0 - light, 1 - dark
#                 width = self.X_DIM * w

#                 #BARS
#                 if kind == '1': #guards
#                     bw = width - self.bar_reduction
#                     _s +=  render_line2(x0=cursor+width/2,y0=self.B_OFFSET+5*self.X_DIM,h=self.X_DIM*33,w=bw)

#                 cursor += width

#         #print first LETTER
#         _s +=  render_letters(self.LEFT_LETTER_OFFSET_X,
#                                 self.LETTER_OFFSET_Y,
#                                 0,
#                                 0,
#                                 str("(01)" + ean_string),
#                                 self.font_name,
#                                 self.font_size)

#         ##print first 6 digits
#         #_s +=  render_letters(self.PREFIX_LETTER_OFFSET_X,
#         #                        self.LETTER_OFFSET_Y,
#         #                        self.LETTER_X_ADD,
#         #                        self.LETTER_Y_ADD,
#         #                        str(ean_string[1:7]),
#         #                        self.font_name,
#         #                        self.font_size)
#         #
#         ##print last 6 digits
#         #_s +=  render_letters(self.SUFFIX_LETTER_OFFSET_X,
#         #                        self.LETTER_OFFSET_Y,
#         #                        self.LETTER_X_ADD,
#         #                        self.LETTER_Y_ADD,
#         #                        str(ean_string[7:]),
#         #                        self.font_name,
#         #                        self.font_size)


#         #DEBUG
#         _s += self.make_debug()

#         #BOUNDARIES
#         _s += self.make_marks()

#         #FOOTER
#         _s +=  render_footer()

#         return _s



