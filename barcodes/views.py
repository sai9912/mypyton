import os
import re
import trml2pdf
from .barcode import Barcode
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from core import jsonify
from django.utils import timezone
from .preview import Preview
from .utilities import Storage, get_completion, make_omlet, generate_download_file
from users.helpers import user_agreement_required
from .generator import get_payload
from .forms import GenerateForm, PreviewFormAjax, FormPS, FormPDF
from .models import label_service

ALLOWED_BARCODE_TYPES = ['EAN13', 'ITF14', 'UPCA']


@user_agreement_required
def barcodes_preview(request, bc_kind, gtin):
    if not re.match('\d{14}', gtin):
        return jsonify(success=False, msg='You entered a non valid GTIN number')
    if bc_kind not in ALLOWED_BARCODE_TYPES:
        return jsonify(success=False, msg='Wrong barcode kind')
    # if bc_kind == 'EAN13':
    #    gtin = gtin[1:14]
    size = 1.00
    bwr = 0.0000
    rqz = 'y'
    marks = ''
    debug = ''
    kind = bc_kind

    # Prefix validation
    prefix = None
    '''
    for prfx in current_user.organisation.prefixes:
        if prfx.is_active:
            prefix = prfx
            break
    if not prefix:
        return jsonify({'success': False, 'msg': 'You do not have an active 
        prefix'})
    if not re.match('[0-9]{%d}' % len(prefix.prefix), prefix.prefix):
        return jsonify({'success': False, 'msg': 'This barcode is not of your 
        active prefix'})
    '''

    data_complete = get_completion(request.user, gtin)

    barcode = Storage({
                          'gtin': str(gtin),
                          'omlet': 'preview',
                          'id': str(gtin),
                          'bwr': bwr,
                          'size': size,
                          'kind': kind,
                          'pmk': marks,
                          'price': None,
                          'name': None,
                          'debug': debug,
                          'rqz': rqz
                      })

    image_preview_path = os.path.join(settings.BARCODES_FILES_PATH,
                                      str(request.user.id), kind)
    image_preview = Preview(request,
                            barcode,
                            debug=debug,
                            watermark=True,
                            path=image_preview_path)

    # Check cache for generated barcode
    if not os.path.exists(image_preview.img_fqn):
        image_preview.generate()

    context = {
        'image': image_preview.image,
        'gtin': gtin,
        'kind': kind,
        'prefix': prefix,
        'points': 0,  # current_user.organisation.credit_points_balance
        'data_compoete': data_complete,
        'barcode_credits':
            request.user.profile.member_organisation.barcode_credits
    }

    return render(request, 'barcodes/preview.html', context)


@user_agreement_required
def barcodes_generate(request, bc_kind, gtin):
    """
    ean-13-generate with ajax
    """
    if bc_kind not in ALLOWED_BARCODE_TYPES:
        return jsonify(success=False, msg='Wrong barcode kind')

    if not request.user.profile.agreed_barcode_disclaimer:
        request.user.profile.agreed_barcode_disclaimer = True
        request.user.profile.agreed_barcode_disclaimer_date = timezone.now()
        request.user.profile.save()

    size = 1.00
    bwr = 0.0000
    rqz = 'y'
    marks = ''
    debug = ''
    ps_type = 'win'
    kind = bc_kind

    '''
    # find barcode object, see if downloadable
    bc = barcode_service.first(user_id=current_user.id, gtin=gtin, kind=kind, 
    downloadable=True)
    if not bc:
        return jsonify({'success': False, 'msg': 'Barcode does not exist'})
    # if bc_kind == 'EAN13':
    #    gtin = gtin[1:14]
    '''

    prefix = None
    '''
    for prfx in current_user.organisation.prefixes:
        if prfx.is_active:
            prefix = prfx
            break
    if not prefix:
        return jsonify({'success': False, 'msg': 'You do not have an active 
        prefix'})
    if prefix.prefix not in gtin:
        return jsonify({'success': False, 'msg': 'This barcode is not of your 
        active prefix'})
    '''

    if request.method == 'POST':
        form = PreviewFormAjax(request.POST)
        if form.is_valid():
            size = float(form.cleaned_data['size'])
            bwr = float(form.cleaned_data['bwr'])
            rqz = form.cleaned_data['rqz']
            marks = form.cleaned_data['marks']
            debug = form.cleaned_data['debug']
    else:
        form = PreviewFormAjax({
                                   'size': '1.00',
                                   'bwr': '0.0000',
                                   'rqz': rqz,
                                   'marks': marks,
                                   'debug': debug
                               })

    '''
    form_ps = GenerateForm(prefix="form_ps-" + kind.lower(), ps_type=ps_type)
    '''

    form_raster = GenerateForm({
                                   'prefix': 'form_raster-' + kind.lower(),
                                   'file_type': 'png',
                                   'resolution': '300 dpi'
                               })

    form_ps = FormPS({'ps_type': 'win'})

    '''
    form_labels = GenerateForm(prefix="form_label-" + kind.lower(), 
    label_type="L7161")

    all_labels = label_service.all()
    form_labels.set_label_types(all_labels)
    '''
    form_labels = FormPDF({'label_type': 'L7161'})

    barcode = Storage({
                          'gtin': str(gtin),
                          'omlet': None,
                          'id': str(gtin),
                          'bwr': bwr,
                          'size': size,
                          'kind': kind,
                          'pmk': marks,
                          'price': None,
                          'name': None,
                          'debug': debug,
                          'rqz': rqz
                      })

    barcode.omlet = make_omlet(barcode)

    image_preview_path = os.path.join(settings.BARCODES_FILES_PATH,
                                      str(request.user.id), kind)
    image_preview = Preview(request,
                            barcode,
                            debug=debug,
                            watermark=False,
                            path=image_preview_path,
                            res=settings.BARCODES_GENERATE_RES)

    img_fn = image_preview.generate()

    image = '/'.join(img_fn.split('/')[-4:])

    context = {
        'form': form,
        'form_raster': form_raster,
        'form_ps': form_ps,
        'form_labels': form_labels,
        'image': image,
        'gtin': gtin,
        'kind': kind,
        'prefix': prefix,
        'labels': None
    }  # all_labels}

    return render(request, 'barcodes/generate.html', context)


@user_agreement_required
def barcodes_image_download(request, bc_kind, gtin, dl_type):
    parameters = request.GET.dict()
    parameters.update({
        'bc_kind': bc_kind,
        'gtin': gtin,
        'dl_type': dl_type,
        'user_id': request.user.id,
    })
    result = generate_download_file(parameters)

    if result.get('success'):
        file_path = result['file_path']
        filename = file_path.split('/')[-1]
        send_file = open(file_path, 'rb')
        response = HttpResponse(send_file)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        if filename.endswith('.png'):
            response['Content-Type'] = 'image/png'
        elif filename.endswith('.gif'):
            response['Content-Type'] = 'image/gif'
        elif filename.endswith('.jpg'):
            response['Content-Type'] = 'image/jpeg'
        elif filename.endswith('.eps'):
            response['Content-Type'] = 'application/postscript'
        elif filename.endswith('.eps.bin'):
            response['Content-Type'] = 'application/postscript'
        elif filename.endswith('.pdf'):
            response['Content-Type'] = 'application/pdf'

        return response
    else:
        # error message
        return jsonify(**result)
