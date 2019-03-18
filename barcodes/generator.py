import os, logging

from django.conf import settings
from .printers import BarcodeManager as bm
from .printers import BarcodeManagerISBN as bm_isbn
from .printers import BarcodeManagerITF as bm_itf14
from .printers import BarcodePrinterUPCA as bp_upca
from .printers import BarcodePrinterEAN13 as bp_ean13
from .printers import BarcodePrinterISBN13 as bp_isbn13
from .printers import BarcodePrinterISBN13AddOn as bp_isbn13ao
from .printers import BarcodePrinterITF14 as bp_itf14
from . import isbn_parser
from .utilities import isValid, check_dir


def get_payload(g, symbol, file_type, static_path='static', resolution=None,
                addon=None, rqz=False, bwr=0.0, scale=1.0, dryrun=False,
                debug=False, marks=False):
    logging.info("* entered get_eps_file *")
    # print static_path

    bwr = 0.0000
    rqz = 'y'

    check_dir(static_path)

    if symbol == 'UPCA':
        symbol = 'upc-a'
        bc_data = g.symbols[symbol]['data']

    if symbol == 'EAN13':
        symbol = 'ean-13'
        bc_data = g.symbols[symbol]['data']

    if symbol == 'ISBN13':
        symbol = 'isbn-13'
        bc_data = g.symbols['ean-13']['data']

    if symbol == 'ITF14':
        symbol = 'itf-14'
        bc_data = g.symbols['itf-14']['data']

    # validate GTIN
    assert isValid(bc_data)

    ps_fn = '%s/%s.ps' % (static_path, bc_data)
    # print ps_fn

    ps_fqn = ps_fn
    logging.debug("ps_fqn: %s" % ps_fqn)

    #TEMP FILE (needed to adjust BB)
    bbeps_fn = '%s/%s_bb.eps' % (static_path, bc_data)
    bbeps_fqn = bbeps_fn
    logging.debug("bbeps_fqn: %s" % bbeps_fqn)

    #EPSTOOL
    eps_fn = '%s/%s.eps' % (static_path, bc_data)
    eps_fqn = eps_fn
    if file_type == 'eps_Mac': eps_fqn += '.bin'
    logging.debug("eps_fqn: %s" % eps_fqn)

    #BITMAP
    image_fn = '%s/%s.%s' % (static_path, bc_data, file_type)
    image_fqn = image_fn
    logging.debug("image_fqn: %s" % image_fqn)

    #config vars
    # marks   = False
    #bwr     = 0.002
    bwr_mm = float(bwr) / 0.03937 / float(scale)

    if dryrun:
        if file_type == 'eps_PC':
            return eps_fqn
        elif file_type == 'eps_Mac':
            return eps_fqn
        elif file_type in ('jpg', 'png', 'gif', 'tif'):
            return image_fqn

    # HERE WE GO
    _generate_ps(g, symbol, marks, scale, bwr_mm, ps_fqn, addon, rqz, debug)
    _generate_bb_file(ps_fqn, bbeps_fqn)

#    _generate_bb_file(ps_fqn, eps_fqn)
#    return eps_fqn

    if file_type == 'eps_PC':
        assert _get_dos_file(bbeps_fqn, eps_fqn)
        return eps_fqn
    elif file_type == 'eps_Mac':
        assert _get_mac_file(bbeps_fqn, eps_fqn)
        return eps_fqn
    elif file_type in ('jpg', 'png', 'gif', 'tif'):
        _generate_bitmap(resolution, ps_fqn, image_fqn)
        return image_fqn

    raise Exception('ops wrong file type %s' % file_type)

#
#################################################################################
# #
# #
# #                             PRIVATE FUNCTIONS
# #
# #
#
#################################################################################
def _generate_ps(g, symbol, marks, scale, bwr_mm, ps_fqn, addon, rqz, debug):
    bc_obj, bc_printer = None, None

    #logging.debug("_generate_ps: %s" % locals())
    logging.debug("_rqz: %s" % str(rqz))

    if symbol == 'upc-a':
        bc_obj = bm.UPCA(g.data12)
        bc_printer = bp_upca.UPCAPrinter(marks=marks, scale=scale,
                                         font_name='OCRZ', font_size=7.5,
                                         bar_reduction=bwr_mm, debug=debug)

    if symbol == 'ean-13':
        bc_obj = bm.EAN13(g.data13)
        bc_printer = bp_ean13.EAN13Printer(marks=marks, scale=scale,
                                           right_limit=rqz,
                                           font_name='OCRZ', font_size=7.5,
                                           bar_reduction=bwr_mm, debug=debug)

    if symbol == 'itf-14':
        bc_obj = bm_itf14.ITF14(g.data14)
        bc_printer = bp_itf14.ITF14Printer(scale=scale,debug=debug) #font_name='OCRZ', font_size=7.5, TODO

    #if symbol == 'databar-14':
    #    bc_obj = rss.RSS14(g.data14,DATABAR)
    #    bc_printer = bp.RSS14Printer(marks=marks,scale=scale,right_limit=rqz,
    #    font_name='OCRZ',font_size=7.5,bar_reduction=bwr_mm)

    if symbol == 'isbn-13':
        rqzi = False

        if addon:
            bc_obj = bm_isbn.ISBN13AddOn(g.data13, addon)
            bc_printer = bp_isbn13ao.ISBN13AddOnPrinter(marks=marks,
                                                        scale=scale,
                                                        right_limit=rqz,
                                                        debug=debug,
                                                        font_name='OCRZ',
                                                        font_size=7.5,
                                                        bar_reduction=bwr_mm)
        else:
            bc_obj = bm_isbn.ISBN13(g.data13)
            bc_printer = bp_isbn13.ISBN13Printer(marks=marks, scale=scale,
                                                 right_limit=rqz, debug=debug,
                                                 font_name='OCRZ',
                                                 font_size=7.5,
                                                 bar_reduction=bwr_mm)

    f = open(ps_fqn, 'w')

    if symbol == "isbn-13":
        hyphens = "ISBN %s" % isbn_parser.hyphenate(bc_obj.arg)[0]
        if not hyphens:
            hyphens = "ISBN %s" % bc_obj.arg

        if addon:
            f.write(bc_printer.work(
                "%s:%s:%s" % (bc_obj.arg, addon, hyphens), bc_obj.data))
        else:
            f.write(
                bc_printer.work("%s:%s" % (bc_obj.arg, hyphens), bc_obj.data))
    else:
        f.write(bc_printer.work(bc_obj.arg, bc_obj.data))

    f.close()
    return


def _generate_bitmap(resolution, ps_fqn, bitmap_fqn):
    logging.debug(">>> _generate_bitmap")
    logging.debug("generating %s from %s with resolution %s" % (
        ps_fqn, bitmap_fqn, resolution))
    bin_convert = settings.BIN_CONVERT
    assert os.path.isfile(ps_fqn)
    cmd = "%s -density %s %s  -background white -flatten -gamma 1.5 %s"
    #convert #density #in #out
    _debug_cmd = cmd % (bin_convert, resolution, ps_fqn, bitmap_fqn)
    logging.debug(">>> %s" % _debug_cmd)
    rc = os.popen(cmd % (bin_convert, resolution, ps_fqn, bitmap_fqn))
    rc.close()
    return


def _generate_bb_file(ps_fqn, bbeps_fqn):
    logging.info('fixing bb first')
    assert os.path.isfile(ps_fqn)
    bin_dir = settings.BIN_DIR
    cmd = '%s/convert_bb.sh %s %s' % (bin_dir, ps_fqn, bbeps_fqn)
    logging.debug(cmd)
    os.system(cmd)
    return True


def _get_mac_file(bbeps_fqn, eps_fqn):
    logging.info('producing mac file')
    bin_dir = settings.BIN_DIR
    rc = os.popen('%s/convert_mac.sh %s %s' % (bin_dir, bbeps_fqn, eps_fqn))
    rc.close()
    return True


def _get_dos_file(bbeps_fqn, eps_fqn):
    logging.info('producing dos file')
    bin_dir = settings.BIN_DIR
    rc = os.popen('%s/convert_dos.sh %s %s' % (bin_dir, bbeps_fqn, eps_fqn))
    rc.close()
    return True

# # This is the command that was previously used for the jpg generation

# #COMMAND = '''%s -q -dBATCH -dMaxBitmap=300000000 -dNOPAUSE -sDEVICE=jpeg \
# #-sFONTPATH=%s/fonts \
# #-dTextAlphaBits=4 -dGraphicsAlphaBits=4 %s \
# #-sOutputFile=%s %s -c quit ''' #exec APP geometry, output, input

# #(stdoutdata, stderrdata) = Popen(['/bin/bash', '-c', "find $(dirname %s)"
# % #f], stdout=PIPE).communicate()
# #logging.debug(stdoutdata)
# #logging.debug(stderrdata)

# #(stdoutdata, stderrdata)  = Popen(['/bin/bash', '-c', cmd],
# stdout=PIPE).communicate()
# #logging.debug(stdoutdata)
# #logging.debug(stderrdata)

# #print >> sys.stderr, '...'
