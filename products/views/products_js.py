import json
import pprint
from decimal import Decimal

from django.conf import settings
from django.core import serializers
from django.http import Http404
from django.middleware import csrf
from django.shortcuts import render, redirect, reverse
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django_jschemer.jsonschema import DjangoFormToJSONSchema

from BCM.helpers import translation_helpers
from BCM.helpers.serialization_helpers import serialize_to_dict
from barcodes.utilities import normalize
from core import flash, flash_get_messages, jsonify
from member_organisations.models import ProductTemplate
from services import prefix_service, product_service, sub_product_service
from users.helpers import user_agreement_required
from ..forms import PackageLevelForm
from ..forms import ProductForm, ProductCaseForm
from ..helpers import subproduct_helper
from ..models.package_level import PackageLevel
from ..models.package_type import PackageType
from ..models.product import Product
from ..utilities import upload_image


@csrf_exempt
@user_agreement_required
def js_add_product(request):
    """
    GET/POST for adding a new base or case product
    :return:
    """

    user_active_prefix = request.user.profile.product_active_prefix
    prefix = request.POST.get('prefix', None)
    if prefix is None:
        prefix = request.GET.get('prefix', None)
    if prefix:
        prefix = prefix_service.find_item(user=request.user, prefix=prefix)
        if prefix and prefix != user_active_prefix:
            prefix_service.make_active(user=request.user, prefix=prefix.prefix)
        if request.session.get('new_product', None):
            del request.session['new_product']
    else:
        prefix = user_active_prefix
    if not prefix:
        flash(request, 'You must have an active prefix set to enter new product. Please choose one', 'danger')
        return redirect(reverse('prefixes:prefixes_list'))
    if not prefix.starting_from:
        flash(request, 'You must have a starting number set to enter new product. Please set one', 'danger')
        return redirect(reverse('prefixes:prefixes_list'))
    if prefix.is_special == 'READ-ONLY':
        flash(
            request, 'You can not add a new product in this range. It\'s a suspended read-only range', 'danger'
        )
        return redirect(reverse('products:products_list'))

    # if prefix.is_special != 'NULL':
    #    package_rows = services.package_level_service.find(
    #        id=models.PACKAGE_LEVEL_SPECIAL_ENUM[prefix.is_special]).all()
    # else:
    #    package_rows = package_level_service.all()
    package_rows = PackageLevel.service.all()

    express = True if request.POST.get('express') or request.GET.get('express') else False

    title = _('New Product')

    if express:
        title = 'Express Allocation'

    if request.method == 'POST':
        form = PackageLevelForm(request.POST)
        form.set_package_levels(package_rows)
        if form.is_valid():
            if not request.session.get('new_product', None):
                request.session['new_product'] = {'gtin': str(prefix.starting_from),
                                                  'package_level': form.data['package_level']}
            elif request.session.get('new_product')['gtin'] != str(prefix.starting_from):
                request.session['new_product'] = {'gtin': str(prefix.starting_from),
                                                  'package_level': form.data['package_level']}
            else:
                request.session['new_product']['package_level'] = form.data['package_level']
            if express:
                request.session['new_product'].update({'express': True})
            elif 'express' in request.session['new_product']:
                del request.session['new_product']['express']
            return redirect(reverse('products:add_product_package_type'))
            # if session['new_product']['package_level'] == str(models.BASE_PACKAGE_LEVEL):
            #    if session['new_product'].get('express'):
            #        return redirect(url_for('products.add_product_express'))
            #    else:
            #        return redirect(url_for('products.add_product_package_type'))
            # else:
            #    return redirect(url_for('products.subproduct_add_case'))
        else:
            flash(request, 'You must choose a level to proceed', 'danger')
    else:
        form = PackageLevelForm()
        form.set_package_levels(package_rows)
        if (
            request.session.get('new_product', None) and
            request.session.get('new_product')['gtin'] == str(prefix.starting_from)
        ):
            form.data['package_level'] = request.session.get('new_product')['package_level']

    package_type_list_qs = PackageType.service.filter(ui_enabled=True).order_by('id').all()
    package_type_list = json.loads(serializers.serialize("json", package_type_list_qs))
    context = {
        'title': title,
        'prefix': prefix,
        'flashed_messages': flash_get_messages(request),
        'form_data_json': json.dumps({
            'mo_slug': prefix.member_organisation.slug,
            'package_type_list': package_type_list,
            'gtin': str(prefix.starting_from),
            'gln_of_information_provider': normalize('EAN13', prefix.prefix),
            'language': translation_helpers.get_current_language(),
            'fallback_languages': settings.FALLBACK_LANGUAGES,
        })
    }

    return render(request, 'products/product_add_js.html', context)


@user_agreement_required
def fulledit_js(request, product_id):
    """
    displays via GET and provides product update mechanics via POST
    :param product_id:
    :return:
    """

    product = Product.service.get_my_product(request.user, product_id)
    prefix = prefix_service.find_item(user=request.user, prefix=product.gs1_company_prefix)

    if not prefix:
        raise Http404()
    if prefix != request.user.profile.product_active_prefix:
        flash(request, 'This product is not in your active prefix', 'danger')
        return redirect(reverse('products:products_list'))

    barcodes = {}
    # for bc in product.barcodes:
    #    barcodes.update({bc.kind: bc})

    if request.GET.get('barcodes'):
        active_tab = 'barcodes'
    elif request.GET.get('cloud'):
        active_tab = 'cloud'
    else:
        active_tab = 'details'

    if prefix.is_upc():
        kind = 'UPCA'
    else:
        kind = 'EAN13'

    pp = pprint.PrettyPrinter(indent=4)
    template_name = 'products/product_fulledit_form_js.html'
    # dev-ui-vue
    context = {'product': product,
               'barcodes': barcodes,
               'active_tab': active_tab,
               'product_id': product_id,
               'pkg_level': product.package_level_id,
               'prefix': prefix,
               'agreed': request.user.profile.agreed,
               'product_image': product.website_url,
               'gtin': product.gtin,
               'gtin0': product.gtin[0:1],
               'gtin13': product.gtin[1:14],
               'product_package_level_id': product.package_level_id,
               'advanced_tab': product.owner.profile.advanced_tab,
               'kind': kind
               }
    # pp.pprint(prefix.__dict__)
    # =======
    #     context = {'product': product,
    #                'barcodes': barcodes,
    #                'active_tab': active_tab,
    #                'product_id': product_id,
    #                'pkg_level': product.package_level_id,
    #                'prefix': prefix,
    #                'agreed': request.user.profile.agreed,
    #                'product_image': product.website_url,
    #                'gtin': product.gtin,
    #                'gtin0': product.gtin[0:1],
    #                'gtin13': product.gtin[1:14],
    #                'product_package_level_id': product.package_level_id,
    #                'advanced_tab': product.owner.profile.advanced_tab,
    #                'kind': kind
    #                }
    # >>>>>>> integration

    # if sub_products:
    #    context.update({'nop': product.number_of_products()})

    # context['sub_products'] = _get_subprods_from_obj(product)

    if request.method == 'POST':
        if product.package_level_id == 70:
            form = ProductForm(request.POST)
        else:
            form = ProductCaseForm(request.POST)

        form_valid = form.is_valid(request)
        if request.FILES:
            upload_image(request, product)

        '''
        _add_field_descriptions(form)
        sub_prods = _get_subprods_from_form(request.form)
        context['sub_products'] = sub_prods


        # if product.package_level_id != 70:
        #    subs_valid = _validate_subprods(sub_prods)
        #    if not subs_valid: form.errors['subProducts'] = ['invalid subproducts']  # FIXME
        # else:

        # we allow for packs without children
        '''
        subs_valid = True

        if form_valid and subs_valid:

            # form_errors = check_values(template_name, form, **context)
            form_errors = None

            if form_errors is not None:
                return form_errors

            gtin = form.data.get('gtin', '')
            context['gtin'] = gtin
            context['gtin0'] = gtin[0:1]
            context['gtin13'] = gtin[1:14]

            if not gtin[1:14].startswith(prefix.prefix):
                flash(request, 'You entered a non valid GTIN number (error #005)', 'danger')
                context['form'] = form
                return render(request, template_name, context=context)

            form_data = {}
            for formfield in form.cleaned_data:
                try:
                    if form.cleaned_data[formfield] != '':
                        form_data[formfield] = form.cleaned_data[formfield]
                    else:
                        pass
                except Exception as e:
                    pass

            # validate presence of subproducts
            # if product.package_level_id != 70 and not sub_prods:
            #    flash('Consider adding sub-products', 'info')

            '''
            form.populate_obj(product)
            img = request.files.get('upload')
            if img:
                try:
                    product.add_image(img)
                    context['product_image'] = product.website_url
                except Exception as e:
                    logging.getLogger().error('Image add error: ' + str(e))
                    flash(str(e), 'danger')
                    return render_template(template_name, form=form, **context)
            '''

            try:
                ### PRODUCT UPDATE UI
                product = Product.service.update(product=product,
                                                 owner=request.user,
                                                 prefix=prefix,
                                                 **form_data)
            except Exception as e:
                flash(request, str(e), 'danger')
                context['form'] = form
                return render(request, template_name, context=context)

            '''
            # subproducts -- update
            for sub_p, quantity, _valid in sub_prods:
                if int(quantity) > 0:
                    sub_p.quantity = quantity
                    services.sub_product_service.save(sub_p)
                else:
                    services.sub_product_service.delete(sub_p)
            flash(_("All changes saved sucessfully"), 'success')
            return redirect(url_for('.fulledit', product_id=product.id))
            '''
        else:
            if product.package_level_id == 70:
                print('ProductFormOptions, errors:', form.errors)
            else:
                print('ProductCaseFormOptions, errors:', form.errors)
    else:  # GET
        form = ProductForm(product)

    schema_repr, alpaca_options = DjangoFormToJSONSchema().convert_to_schema(form)
    form_data = schema_repr['properties']
    form_data['gtin']['type'] = 'hidden'
    form_data['bar_placement']['type'] = 'hidden'
    form_data['package_level']['type'] = 'hidden'
    form_data['package_type']['type'] = 'hidden'

    for field in form:
        value = field.value()
        form_data[field.name]['errors'] = field.errors
        if value is not None:
            if field.name == 'package_level' and hasattr(value, '__dict__'):
                value = value.__dict__.copy()
                value.pop('_state', None)
            if isinstance(value, Decimal):
                form_data[field.name]['value'] = str(value)
            else:
                form_data[field.name]['value'] = value
        if 'enum' in form_data[field.name]:
            form_data[field.name]['enum'] = []
            for choice in field.field.widget.choices:
                form_data[field.name]['enum'].append([choice[0], choice[1]])
        form_data[field.name]['required'] = field.field.required
    context['form'] = form
    package_type_list_qs = PackageType.service.filter(ui_enabled=True).order_by('id').all()
    package_type_list = json.loads(serializers.serialize("json", package_type_list_qs))
    product_template = ProductTemplate.objects.filter(
        package_level=product.package_level,
        member_organisation=product.member_organisation
    ).first()

    js_ref_obj = {
        'csrf': csrf.get_token(request),
        'form_data': form_data,
        'advanced_tab': product.owner.profile.advanced_tab,
        'active_tab': active_tab,
        'enable_leading': False,
        'prefix': prefix.prefix,
        'prefix_is_special': prefix.is_special,
        'mo_slug': prefix.member_organisation.slug,
        'kind': kind,
        'agreed': request.user.profile.agreed,
        'product': serialize_to_dict(product, fields_only=True),
        'product_template_id': product_template.id if product_template else None,
        'user_company': None,
        'barcodes': barcodes,
        'package_type_list': package_type_list,
        'language': translation_helpers.get_current_language(),
        'fallback_languages': settings.FALLBACK_LANGUAGES,
    }

    context['form_data_json'] = json.dumps(js_ref_obj)

    # Hardcode user token into the template for the time being
    # token = AuthToken.objects.create(request.user)  # create knox token for UI
    # print('created token: %s' % token)
    # context['auth_token'] = token

    return render(request, template_name, context=context)


@user_agreement_required
def ajax_get_subproducts_by_gtin(request, gtin):
    product = product_service.get_by_gtin(request.user, gtin)
    associated = sub_product_service.get_associated(product)
    subproducts = []
    for item in associated:
        subproducts.append({'gtin': item.sub_product.gtin,
                            'package_level': item.sub_product.package_level.unit_descriptor,
                            'product_description': item.sub_product.description,
                            'quantity': item.quantity})
    return jsonify(status='Ok', subproducts=subproducts)
