import os

from logging import getLogger
from django.conf import settings


from .printers import BarcodeManager as bm
from .printers import BarcodeManagerISBN as bm_isbn
from .printers import BarcodeManagerITF as bm_itf
from .printers import BarcodePrinterUPCA as bp_upca
from .printers import BarcodePrinterEAN13 as bp_ean13
from .printers import BarcodePrinterISBN13 as bp_isbn13
from .printers import BarcodePrinterISBN13AddOn as bp_isbn13ao
from .printers import BarcodePrinterITF14 as bp_itf14
from . import isbn_parser
from .utilities import isValid


"""Preview class: takes Barcode dictionary and creates images with requested
resolution in specific directory

"""


class Preview(object):
    def __init__(self, request, barcode, debug=False, watermark=True,
                 path=None, res=None):
        logger = getLogger()
        self.request = request
        self.barcode = barcode

        # validate GTIN
        assert isValid(self.barcode.gtin)

        self.extension = settings.BARCODES_PREVIEW_EXT
        self.static = path
        self.watermark = watermark
        self.debug = debug
        if res:
            self.res = res
        else:
            self.res = settings.BARCODES_PREVIEW_RES

        # check that the dir exists
        if not os.path.exists(self.static):
            os.makedirs(self.static)
        self.convert_cmd = "%s -density %s %s -background white -flatten " \
                           "-gamma 1.5 -trim %s" #convert #density #in #out (
        # CMD2)
        self.composite_cmd = "%s -gravity center %s %s %s" #composite #over
        #under #result (CMD2)

        self.convert_bin = settings.BIN_CONVERT
        self.composite_bin = settings.BIN_COMPOSITE
        #filenames
        self.bc_data = self.barcode.gtin
        self.ps_fqn = '%s/%s_%s.ps' % (
            self.static, self.bc_data, self.barcode.omlet)
        self.img_fqn = '%s/%s_%s.%s' % (
            self.static, self.bc_data, self.barcode.omlet, self.extension)
        self.image = '/'.join(self.img_fqn.split('/')[-4:])
        self.overlay_img = settings.BARCODES_OVERLAY_IMAGE

        # logger.debug('preview - working barcode %s' % str(self.barcode.id))
        # logger.debug(self.ps_fqn)
        # logger.debug(self.img_fqn)

        #regenerate?
        self.recreate_ps = True
        self.recreate_img = True

    def generate(self):
        logger = getLogger()
        bwr_mm = float(self.barcode.bwr) / 0.03937 / float(self.barcode.size)
        bc_obj, bc_printer = None, None

        if self.barcode.kind == 'ITF14':
            bc_obj = bm_itf.ITF14(self.bc_data)
            bc_printer = bp_itf14.ITF14Printer(marks=self.barcode.pmk,
                                              debug=self.debug,
                                              scale=float(self.barcode.size),
                                              font_name='OCRZ', font_size=7.5,
                                              bar_reduction=bwr_mm,
                                              watermark=self.watermark)
        if self.barcode.kind == 'UPCA':
            bc_obj = bm.UPCA(self.bc_data[2:14])
            bc_printer = bp_upca.UPCAPrinter(marks=self.barcode.pmk,
                                             debug=self.debug,
                                             scale=float(self.barcode.size),
                                             font_name='OCRZ', font_size=7.5,
                                             bar_reduction=bwr_mm,
                                             watermark=self.watermark)

        if self.barcode.kind == 'EAN13':
            bc_obj = bm.EAN13(self.bc_data[1:14])
            bc_printer = bp_ean13.EAN13Printer(
                debug=self.debug, marks=self.barcode.pmk,
                scale=float(self.barcode.size), font_name='OCRZ',
                font_size=7.5, bar_reduction=bwr_mm,
                right_limit=self.barcode.rqz,
                watermark=self.watermark)

        if self.barcode.kind == 'ISBN13':
            if self.barcode.price:
                bc_obj = bm_isbn.ISBN13AddOn(self.bc_data[1:14], self.barcode.price)
            else:
                bc_obj = bm_isbn.ISBN13(self.bc_data)

            try:
                hyphens = "ISBN %s" % isbn_parser.hyphenate(bc_obj.arg)[0]
            except TypeError as e:
            #pragma: no cover
                hyphens = "ISBN %s" % bc_obj.arg
                #pragma: no cover

            if not hyphens:
            #pragma: no cover
                hyphens = "ISBN %s" % bc_obj.arg  #pragma: no cover

            logger.debug(self.barcode.rqz)

            if self.barcode.price:
                logger.debug('see price')
                temp = "%s:%s:%s" % (bc_obj.arg, self.barcode.price, hyphens)
                bc_printer = bp_isbn13ao.ISBN13AddOnPrinter(
                    marks=self.barcode.pmk,
                    scale=float(self.barcode.size),
                    font_name='OCRZ',
                    font_size=7.5,
                    bar_reduction=bwr_mm,
                    right_limit=self.barcode.rqz,
                    debug=self.debug,
                    watermark=self.watermark)
            else:
                logger.debug('do not see price')
                temp = "%s:%s" % (bc_obj.arg, hyphens)
                bc_printer = bp_isbn13.ISBN13Printer(
                    marks=self.barcode.pmk,
                    scale=float(self.barcode.size),
                    font_name='OCRZ',
                    font_size=7.5,
                    bar_reduction=bwr_mm,
                    right_limit=self.barcode.rqz,
                    debug=self.debug,
                    watermark=self.watermark)

            bc_obj.arg = temp

        assert bc_obj
        assert bc_printer

        #create postscript
        if self.recreate_ps:
            f = open(self.ps_fqn, 'w')
            ps_content = bc_printer.work(bc_obj.arg, bc_obj.data)
            f.write(ps_content)
            f.close()

        #create image
        if self.recreate_img:
            cmd = self.convert_cmd % (self.convert_bin, self.res, self.ps_fqn, self.img_fqn)
            rc = os.popen( cmd )
            rc.close()

        ret = self.img_fqn

        logger.debug(ret)
        return ret
