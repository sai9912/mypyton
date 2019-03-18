import tempfile
from zipfile import ZipFile
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from services import prefix_service
from core import flash
from users.helpers import user_agreement_required
from .forms import ExportForm, ImportForm
from .spreadsheet import export_range, import_products
# from member_organisations.models import ProductTemplate


@user_agreement_required
def excel_export_select(request):
    prefix_prefix = prefix_service.get_active(user=request.user)
    if prefix_prefix:
        prefix = prefix_service.find_item(
            user=request.user, prefix=prefix_prefix)
    else:
        flash(request, 'You must have an active prefix to be able to export product data', 'danger')
        return redirect(reverse('prefixes:prefixes_list'))
    if request.method == 'POST':
        form = ExportForm(
            request.POST,
            queryset=request.user.profile.get_available_templates()
        )
        if form.is_valid():
            export_type = form.cleaned_data['export_type']
            file_type = form.cleaned_data['file_type']
            gepir_export = form.cleaned_data['gepir_export']
            template = form.cleaned_data["available_templates"]

            tfile = tempfile.NamedTemporaryFile(suffix='.%s' % file_type)
            zfile = tempfile.NamedTemporaryFile(suffix='.zip')
            attachment_filename = ''
            try:
                if export_type != 'GTIN':
                    # we presume that products are being downloaded
                    if file_type == 'xlsx':
                        errors = export_range(
                            export_type,
                            gepir_export,
                            file_type,
                            tfile.name,
                            prefix,
                            request.user,
                            template
                        )
                        with ZipFile(zfile.name, "w") as z:
                            if gepir_export:
                                export_filename = "gepir_export_%s_%s.%s" % (
                                    prefix.prefix, export_type, file_type)
                                attachment_filename = "gepir_export_%s_%s.%s" % (
                                    prefix.prefix, export_type, 'zip')
                            else:
                                export_filename = "export_%s_%s.%s" % (
                                    prefix.prefix, export_type, file_type)
                                attachment_filename = "export_%s_%s.%s" % (
                                    prefix.prefix, export_type, 'zip')
                            z.write(tfile.name, export_filename)
                            if errors and len(errors) != 0:
                                efile = tempfile.NamedTemporaryFile(
                                    suffix='.txt')
                                with open(efile.name, "w") as error_file:
                                    for error in errors:
                                        for gtin, field_errors in error.items():
                                            error_file.write(
                                                "Product %s errors:\r\n" % gtin)
                                            error_keys = list(
                                                field_errors.keys())
                                            error_keys.sort()
                                            # for field, field_error in field_errors.items():
                                            for key in error_keys:
                                                field, field_error = key, field_errors.get(
                                                    key)
                                                error_file.write(
                                                    "\t%s: %s\r\n" % (field, field_error))
                                            error_file.write("\r\n")
                                z.write(efile.name, "errors_%s_%s.%s" %
                                        (prefix.prefix, export_type, 'txt'))
                        send_file = open(zfile.name, 'rb')
                        response = HttpResponse(
                            send_file, content_type='application/zip')
                        response['Content-Disposition'] = 'attachment; filename=%s' % attachment_filename
                        return response

                    # for debugging ...
                    elif file_type == 'json':
                        pass
                        '''
                        errors = export_range(export_type, gepir_export, file_type, tfile.name, prefix, current_user)
                        if errors and len(errors) != 0:
                            data_in = None
                            with open(tfile.name, 'r') as json_in:
                                data_in = json.loads(json_in.read())
                                # print 'data:', data_in
                                json_in.close()
                            with open(tfile.name, 'w') as json_out:
                                data_in.update({'errors': errors})
                                json_out.write(json.dumps(data_in))
                                # print 'data+errors:', data_in
                                json_out.close()
                        return send_file(tfile, mimetype='application/json',
                                         as_attachment=True,
                                         attachment_filename=attachment_filename)
                        '''
                    else:
                        raise Exception(f'Unsupported file type {file_type}')
            except Exception as e:
                flash(request, 'Error: %s' % str(e), 'danger')
    else:
        form = ExportForm(
            queryset=request.user.profile.get_available_templates())
        # if prefix.get_capacity() > 1000:
        #    form.file_type.choices = (('csv', 'Comma seperated file csv'),)

    context = {'prefix': prefix, 'form': form}
    return render(request, 'excel/export_select.html', context=context)


def excel_import_file(request):
    def validate_file(filename):
        ALLOWED_EXTENSIONS = {'xls', 'xlsx', 'ods', 'csv'}
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    prefix_prefix = prefix_service.get_active(user=request.user)
    if prefix_prefix:
        prefix = prefix_service.find_item(
            user=request.user, prefix=prefix_prefix)
    else:
        flash(request, 'You must have an active prefix to be able to import product data', 'danger')
        return redirect(reverse('prefixes:prefixes_list'))

    if request.method == 'POST':
        imp_file = request.FILES['import_file']
        if imp_file and validate_file(imp_file.name):
            ext = imp_file.name.rsplit('.', 1)[1]
            tfile = tempfile.NamedTemporaryFile(
                suffix=".%s" % ext, delete=False)
            for chunk in imp_file.chunks():
                tfile.write(chunk)
            tfile.close()
            # try:
            errors = import_products(prefix, request.user, tfile.name, request)
            if errors and len(errors) != 0:
                zfile = tempfile.NamedTemporaryFile(suffix='.zip')
                with ZipFile(zfile.name, 'w') as z:
                    efile = tempfile.NamedTemporaryFile(suffix='.txt')
                    with open(efile.name, 'w') as error_file:
                        for error in errors:
                            for label, field_errors in error.items():
                                error_file.write('%s: \r\n' % label)
                                for field, field_error in field_errors.items():
                                    error_file.write(
                                        '\t%s: %s\r\n' % (field, field_error))
                                error_file.write('\r\n')
                    z.write(efile.name, 'import_errors.txt')
                try:
                    prefix.make_starting_from()
                except Exception as ex:
                    prefix.starting_from = None
                finally:
                    prefix_service.save(prefix)
                send_file = open(zfile.name, 'rb')
                response = HttpResponse(
                    send_file, content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename="import_errors.zip"'
                return response
            else:
                flash(request, 'Import completed with no errors', 'success')
            return redirect(reverse('products:products_list'))

    form = ImportForm()
    context = {'prefix': prefix, 'form': form}
    return render(request, 'excel/import_file.html', context=context)
