import json
import logging
import os
import trml2pdf

from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.core.serializers import serialize
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, reverse
from django.template.loader import get_template
from django.utils import translation
from django.utils.translation import gettext as _

from BCM.helpers.pdf_export import render_to_pdf
from barcodes.utilities import normalize
from core import flash, flash_get_messages, jsonify
from products.helpers.product_helper import get_static_file_full_path, is_valid_url
from products.models import TargetMarket
from services import prefix_service
from services import sub_product_service
from services import country_of_origin_service, target_market_service, language_service
from services import gtin_target_market_service
from users.helpers import user_agreement_required
from ..forms import PackageLevelForm, PackageTypeForm, FilterForm
from ..forms import ProductDetailForm
from ..forms import ProductForm, ProductCaseForm
from ..helpers import product_helper, subproduct_helper
from ..models.package_level import PackageLevel
from ..models.package_type import PackageType
from ..models.product import Product
from ..models.sub_product import SubProduct
from ..utilities import delete_product_image, get_image_dimensions, upload_image
from member_organisations.models import ProductTemplate


@user_agreement_required
def add_product(request):
    """
    GET/POST for adding a new base or case product
    :return:
    """
    subproduct_helper.subproducts_reset(request.session)  # remove subproducst from session if any
    user_active_prefix = request.user.profile.product_active_prefix
    prefix = request.POST.get('prefix', None)

    if prefix is None:
        prefix = request.GET.get('prefix', None)
    if prefix:
        prefix = prefix_service.find_item(user=request.user, prefix=prefix)
        if prefix and prefix != user_active_prefix:
            prefix_service.make_active(prefix.prefix, request.user)
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
        flash(request, 'You can not add a new product in this range. It\'s a suspended read-only range', 'danger')
        return redirect(reverse('products:products_list'))

    package_rows = PackageLevel.service.all()
    express = True if request.POST.get('express') or request.GET.get('express') else False

    title = 'New Product'
    if express:
        title = 'Express Allocation'

    if request.method == 'POST':
        form = PackageLevelForm(request.POST)
        form.set_package_levels(package_rows)
        if form.is_valid():
            try:
                prefix.make_starting_from()
            except Exception:
                flash(request, 'not allowed to create products for this prefix.', 'danger')
                return redirect(reverse('prefixes:prefixes_list'))

            if not request.session.get('new_product', None):
                request.session['new_product'] = {
                    'gtin': prefix.starting_from,
                    'package_level': form.data['package_level']
                }
            elif request.session['new_product'].get('gtin') != prefix.starting_from:
                request.session['new_product'] = {
                    'gtin': prefix.starting_from,
                    'package_level': form.data['package_level']
                }
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
        if (request.session.get('new_product', None) and
                request.session['new_product'].get('gtin') == prefix.starting_from):
            form.data['package_level'] = request.session.get('new_product')['package_level']

    templates = ProductTemplate.objects.filter(
        member_organisation=request.user.profile.member_organisation
    ).order_by('order')

    context = {'title': title,
               'prefix': prefix,
               'templates': templates
               }

    return render(request, 'products/package_level_form.html', context)


@user_agreement_required
def add_product_package_type(request):
    """
    package type selector
    :return:
    """
    session = request.session.get('new_product', None)
    if not session:
        raise Http404('Session does not exist')
    gtin = session.get('gtin', None)
    if not gtin:
        raise Http404('No gtin in session')
    prefix = prefix_service.find_item(user=request.user, starting_from=str(gtin))
    if not prefix:
        raise Http404('Starting prefix (%s) not found' % prefix)

    if request.method == 'POST':
        form = PackageTypeForm(request.POST, prefix=prefix)
        if form.is_valid():
            request.session['new_product'].update({
                'package_type': form.cleaned_data['package_type'],
                'bar_placement': form.cleaned_data['bar_placement']
            })
            if session.get('package_level') == '70':
                return redirect(reverse('products:add_product_base_details'))
            else:
                return redirect(reverse('products:subproduct_add_case'))
    else:
        form = PackageTypeForm(prefix=prefix)
        if session.get('package_level') == '70':
            form.initial['bar_placement'] = settings.STATIC_URL + 'products/site/wizard/proddesc/BG.png'
            form.initial['package_type'] = '1'
        else:
            form.initial['bar_placement'] = settings.STATIC_URL + 'products/site/wizard/proddesc/CS.png'
            form.initial['package_type'] = '34'

    if session.get('package_level') == '70':
        package_level = 'Base Unit / Each'
    elif session.get('package_level') == '60':
        package_level = 'Pack or inner pack'
    elif session.get('package_level') == '50':
        package_level = 'Case or mixed case'
    elif session.get('package_level') == '40':
        package_level = 'Display unit'
    else:
        package_level = 'Pallet'  # 30

    context = {
        'form': form,
        'prefix': prefix,
        'package_types': PackageType.service.filter(ui_enabled=True).order_by('id'),
        'package_level': package_level
    }
    return render(request, 'products/package_type_form.html', context=context)


@user_agreement_required
def add_product_base_details(request):
    """
     -- used for the NEW (Step 2 - EACH)
    GET / POST for adding a base level item
    :template_name: products/product_details_form.html
    :return:
    """

    session = request.session.get('new_product', None)
    if not session:
        raise Http404()
    for k in ['package_type', 'package_level', 'gtin', 'bar_placement']:  # Check session and restart if missing
        if k not in session.keys():
            del request.session['new_product']
            flash(request, 'Add new product restarted #010', 'danger')
            return redirect(reverse('products:add_product'))

    gtin = session.get('gtin', '0')

    prefix = prefix_service.find_item(user=request.user, starting_from=gtin)
    if not prefix:
        raise Http404()
    if prefix.is_upc():
        kind = 'UPCA'
    else:
        kind = 'EAN13'

    if request.method == 'POST':
        context_is_new = 0
        post_data = request.POST.dict()

        form = ProductDetailForm(data=post_data)

        verified = True
        if not form.data.get('gtin', '')[1:14].startswith(prefix.prefix):
            flash(request, 'You entered a non valid GTIN number (error #001)', 'danger')
            verified = False
        if not form.is_valid(request):
            verified = False
        if verified:
            form_data = {}
            for formfield in form.cleaned_data:
                try:
                    if formfield == 'csrfmiddlewaretoken':
                        continue
                    if form.data[formfield] != '':
                        form_data[formfield] = form.cleaned_data[formfield]
                    else:
                        pass
                except Exception as e:
                    pass

            try:
                ### PRODUCT CREATE UI
                with translation.override(form_data.get('language', 'en')):
                    product = Product.service.create(
                        owner=request.user,
                        company_organisation=prefix.company_organisation,
                        prefix=prefix,
                        **form_data
                    )
            except Exception as e:
                flash(request, str(e), 'danger')
                return redirect(reverse('products:add_product_base_details'))

            # Load image
            if request.FILES:
                upload_image(request, product)

            # Update prefix
            try:
                prefix.increment_starting_from()
                prefix_service.save(prefix)
            except Exception as e:
                flash(request, str(e), 'danger')

            if request.session.get('new_product'):
                del request.session['new_product']

            return redirect(reverse('products:view_product_summary', args=(product.id,)))
        else:
            logging.debug('ProductDetailFormOptions error: %s' % str(form.errors))
    else:
        context_is_new = 1
        form = ProductDetailForm()
        # default values - new product GET
        form.initial['gln_of_information_provider'] = normalize('EAN13', prefix.prefix)
        form.initial['is_bunit'] = True
        form.initial['company'] = prefix.company_organisation.company

    form.initial['gtin'] = '0' + session.get('gtin')
    form.initial['bar_placement'] = session.get('bar_placement')
    form.initial['package_level'] = session.get('package_level')
    form.initial['package_type'] = session.get('package_type')
    form.initial['image'] = session.get('image', settings.NO_IMAGE)

    country = request.user.profile.member_organisation.country
    country_of_origin = country_of_origin_service.find_by_country(country)
    if country_of_origin:
        form.initial['country_of_origin'] = country_of_origin.code

    target_market = target_market_service.find_by_country(country)
    if target_market:
        form.initial['target_market'] = target_market.code

    language_slug = request.user.profile.language
    language = language_service.find_by_slug(language_slug)
    if language:
        form.initial['language'] = language.slug
    form.initial['category'] = 'asdfasdf'

    context = {'title': 'New Base Unit / Each (Step 2 of 2: Details)',
               'is_new': context_is_new,
               'prefix': prefix,
               'gtin0': '0',
               'gtin13': session['gtin'],
               'kind': kind,
               'product_package_level_id': int(session['package_level']),
               'leading_gln': normalize('EAN13', prefix.prefix),
               'form': form,
               'flashed_messages': flash_get_messages(request)}
    return render(request, 'products/product_details_form.html', context=context)


@user_agreement_required
def view_product_summary(request, product_id):
    product = Product.service.get_my_product(request.user, product_id)

    prefix = prefix_service.find_item(user=request.user, prefix=product.gs1_company_prefix)
    if not prefix:
        raise Http404()

    sub_products = sub_product_service.get_associated(product)
    nop = None
    if product.package_level.id == PackageLevel.BASE:
        title = 'New Base Unit / Each (Summary)'
    else:
        title = 'New item (Summary)'
        nop = len(sub_products)

    is_xhr = request.GET.get('xhr', False) and True
    if is_xhr:
        template_name = 'products/product_summary_xhr.html'
    else:
        template_name = 'products/product_summary.html'

    product_fields = []
    product_fields_list = product._meta.get_fields()
    for field in product_fields_list:
        product_fields.append({'name': field.name, 'value': getattr(product, field.name)})

    context = {
        'title': title,
        'prefix': prefix,
        'product': product,
        'product_fields': product_fields,
        'nop': nop,
        'sub_products': sub_products,
        'debug': False
    }
    return render(request, template_name, context=context)


# deprecated
@user_agreement_required
def products_list(request):
    user_active_prefix = request.user.profile.product_active_prefix
    if request.GET.get('prefix'):
        prefix = prefix_service.find_item(user=request.user, prefix=request.GET.get('prefix'))
        if prefix and prefix != user_active_prefix:
            prefix_service.make_active(prefix.prefix, user=request.user)
        elif not prefix:
            flash(request, 'Incorrect active prefix. Please choose one', 'danger')
            return redirect(reverse('prefixes:prefixes_list'))
    else:
        prefix = user_active_prefix
        if not prefix:
            flash(request, 'You must have an active prefix to see products. Please choose one', 'danger')
            return redirect(reverse('prefixes:prefixes_list'))

    try:
        page = int(request.GET.get('page', '1'))
    except (ValueError, TypeError):
        page = 1

    try:
        settings_per_page = settings.PRODUCTS_PER_PAGE
    except:
        settings_per_page = 10
    try:
        per_page = int(request.GET.get('per_page'))
    except (ValueError, TypeError):
        per_page = None
    if per_page:
        request.session['per_page'] = per_page
    else:
        per_page = request.session.get('per_page', settings_per_page)

    all_in_range = Product.objects.filter(
        company_organisation=request.user.profile.company_organisation,
        gs1_company_prefix=prefix.prefix
    )

    target_market_ids = all_in_range.values_list('target_market', flat=True).distinct()
    target_markets = TargetMarket.objects.filter(id__in=target_market_ids)

    target_market_choices = [['', '']]
    for target_market in target_markets:
        try:
            if target_market_choices[-1][0] == target_market.code:
                continue
        except Exception:
            pass
        target_market_choices.append([target_market.code, target_market.market])

    completeness = product_helper.get_completeness(all_in_range)

    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            all_in_range = product_helper.filter_list(all_in_range, form)
            request.session['list_filter'] = product_helper.make_filter(form)
        else:
            logging.getLogger().debug(str(form.errors))
    else:
        if request.GET.get('clear_filter'):
            if request.session.get('list_filter'):
                del request.session['list_filter']
        if request.session.get('list_filter'):
            try:
                form = FilterForm(request.session['list_filter'])
                all_in_range = product_helper.filter_list(all_in_range, form)
            except:
                del request.session['list_filter']
                form = FilterForm()
        else:
            form = FilterForm()

    # if sort arguments are provided in GET we will override them
    # see https://github.com/tbikeev/robot-gs1/issues/30

    if request.GET.get('sort_mode') and request.GET.get('sort_field'):
        form.data['sort_field'] = request.GET.get('sort_field')
        form.data['sort_mode'] = request.GET.get('sort_mode')

    sort_field = form.data.get('sort_field', form.fields['sort_field'].initial)
    sort_mode = form.data.get('sort_mode', form.fields['sort_mode'].initial)
    if sort_mode == 'desc':
        sort_order = '-%s' % sort_field
        sort_mode = 'Descending'
    else:
        sort_order = sort_field
        sort_mode = 'Ascending'
    for key, value in form.fields['sort_field'].choices:
        if sort_field == key:
            sort_field = value
            break

    products = all_in_range.order_by(sort_order)
    paginator = Paginator(products, per_page)
    try:
        paginator_page = paginator.page(page)
    except InvalidPage:
        paginator_page = paginator.page(1)

    form.fields['target_market'].choices = target_market_choices
    form.base_fields['target_market'].choices = target_market_choices
    form.declared_fields['target_market'].choices = target_market_choices

    templates = {}
    for item in ProductTemplate.objects.filter(member_organisation=request.user.profile.member_organisation):
        templates[ item.package_level_id ] = True

    assoc_products = []
    for p in paginator_page.object_list:
        if p.package_level.id != 70:
            subproducts = SubProduct.objects.filter(product=p).all()
            sub_p = []
            for subproduct in subproducts:
                sub_product = subproduct.sub_product
                sub_p.append({'id': sub_product.id,
                              'package_level': {'id': sub_product.package_level_id},
                              'brand': sub_product.brand,
                              'description': sub_product.description,
                              'gtin': sub_product.gtin,
                              'gs1_company_prefix': sub_product.gs1_company_prefix,
                              'bar_type': sub_product.bar_type,
                              'quantity': subproduct.quantity})
            assoc_products.append({'p_id': p.id,
                                   'sub_p': sub_p})

    context = {'prefix': prefix,
               'latest_product_list': paginator_page.object_list,
               'assoc_products': assoc_products,
               'pagination': paginator_page,
               'per_page': per_page,
               'ppp': settings_per_page,
               'sorted': {'field': sort_field, 'mode': sort_mode},
               'form': form,
               'enable_leading': True,      # request.user.enable_leading
               'templates': templates,
               'completeness': completeness}

    return render(request, 'products/list.html', context=context)

@user_agreement_required
def products_list_js(request):
    user_active_prefix = request.user.profile.product_active_prefix
    if request.GET.get('prefix'):
        prefix = prefix_service.find_item(user=request.user, prefix=request.GET.get('prefix'))
        if prefix and prefix != user_active_prefix:
            prefix_service.make_active(prefix.prefix, user=request.user)
        elif not prefix:
            flash(request, 'Incorrect active prefix. Please choose one', 'danger')
            return redirect(reverse('prefixes:prefixes_list'))
    else:
        prefix = user_active_prefix
        if not prefix:
            flash(request, 'You must have an active prefix to see products. Please choose one', 'danger')
            return redirect(reverse('prefixes:prefixes_list'))

    templates = {}
    for item in ProductTemplate.objects.filter(member_organisation=request.user.profile.member_organisation):
        templates[item.package_level_id] = True

    all_in_range = Product.objects.filter(
        company_organisation=request.user.profile.company_organisation,
        gs1_company_prefix=prefix.prefix
    )
    completeness = product_helper.get_completeness(all_in_range)
    context = {
        'prefix': prefix,
        'templates': templates,
        'completeness': completeness
    }
    return render(request, 'products/list_js.html', context=context)



@user_agreement_required
def ajax_product_mark(request, product_id):
    """
    makes product marked
    """
    product = Product.service.get(id=product_id)
    product.mark = 1
    product.save()
    return jsonify(success=True)


@user_agreement_required
def ajax_product_unmark(request, product_id):
    """
    makes product un-marked
    """
    product = Product.service.get(id=product_id)
    product.mark = 0
    product.save()
    return jsonify(success=True)


@user_agreement_required
def ajax_get_package_type(request, package_type_id):

    try:
        package_type = PackageType.objects.get(id=package_type_id)
    except PackageType.DoesNotExist:
        raise Http404()
    else:
        package_type_json = serialize('json', [package_type])
        package_type_json = json.loads(package_type_json)[0]['fields']
        package_type_json['type'] = package_type.type
        package_type_json['description'] = package_type.description
        return jsonify(package_type=package_type_json)


@user_agreement_required
def product_print_summary(request, product_id):
    product = Product.service.get(id=product_id)
    sub_products = sub_product_service.get_associated(product)
    nop = len(sub_products)

    templates = dict()
    product_templates = ProductTemplate.objects.filter(
        member_organisation=request.user.profile.member_organisation
    ).all()

    for product_template in product_templates:
        ui_label_i18n = json.loads(product_template.ui_label_i18n)
        try:
            templates[product_template.package_level_id] = ui_label_i18n[request.user.profile.language]
        except:
            try:
                templates[product_template.package_level_id] = ui_label_i18n['en']
            except:
                pass
    for sub_product in sub_products:
        try:
            sub_product.ui_label = templates[sub_product.sub_product.package_level_id]
        except:
            sub_product.ui_label = sub_product.sub_product.package_level.level

    logo = request.user.profile.member_organisation.gs1_logo_path
    if not logo:
        logo = 'static/site/logo/gs1-logo.png'
    else:
        logo = logo[1:]
    logo = logo.replace('logo/', 'logo/pdf/')

    product_template = ProductTemplate.objects.filter(
        package_level=product.package_level,
        member_organisation=product.member_organisation
    ).first()

    context = {
        'logo': logo,
        'verdana': 'static/site/fonts/verdana.ttf',
        'verdana_bold': 'static/site/fonts/verdanab.ttf',
        'product': product,
        'sub_products': sub_products,
        'nop': nop,
        # ui configuration for the main product (to show/hide required fields and so on)
        'ui_attributes': getattr(product_template, 'attributes_dict', None),
    }
    try:
        p_width, p_height = get_image_dimensions('products' + product.bar_placement)
        k_width = p_width / 40
        k_height = p_height / 40
        if k_width > k_height:
            p_width = int(p_width / k_width)
            p_height = int(p_height / k_width)
        else:
            p_width = int(p_width / k_height)
            p_height = int(p_height / k_height)
        context.update({'placement': 'products' + product.bar_placement,
                        'p_height': p_height,
                        'p_width': p_width})
    except Exception as e:
        package_level = product.package_level.id
        bar_placement = PackageLevel.BAR_PLACEMENT[package_level]
        p_width, p_height = get_image_dimensions(bar_placement)
        k_width = p_width / 40
        k_height = p_height / 40
        if k_width > k_height:
            p_width = int(p_width / k_width)
            p_height = int(p_height / k_width)
        else:
            p_width = int(p_width / k_height)
            p_height = int(p_height / k_height)
        context.update({'placement': bar_placement,
                        'p_height': p_height,
                        'p_width': p_width})

    try:

        if is_valid_url(product.image):
            image_path = product.image
        else:
            image_path = get_static_file_full_path(product.image)

        i_width, i_height = get_image_dimensions(image_path)
        k_width = i_width / 40
        k_height = i_height / 402
        if k_width > k_height:
            i_width = int(i_width / k_width)
            i_height = int(i_height / k_width)
        else:
            i_width = int(i_width / k_height)
            i_height = int(i_height / k_height)
        context.update({'image': image_path,
                        'i_width': i_width,
                        'i_height': i_height})
    except Exception as e:
        pass

    # reportlab variant
    # template_name = 'products/product_print_summary.rml'
    # pdf_template = str(get_template(template_name).render(context))
    # pdf = trml2pdf.parseString(pdf_template.encode('utf-8'))

    # secretary variant
    pdf = render_to_pdf(
        template_name='products/templates/products/product_print_summary.odt',
        context=context
    )
    response = HttpResponse(pdf, content_type='application/pdf')

    # display pdf in place
    response['Content-Disposition'] = 'inline; filename="%s.pdf"' % product.gtin

    # as attachment ("download as.."):
    # response['Content-Disposition'] = 'attachment; file   name="%s.pdf"' % product.gtin
    return response


@user_agreement_required
def fulledit(request, product_id):
    """
    displays via GET and provides product update mechanics via POST
    :param product_id:
    :return:
    """

    product = Product.service.get_my_product(request.user, product_id)
    if not product:
        raise Http404()

    prefix = prefix_service.find_item(user=request.user, prefix=product.gs1_company_prefix)
    user_active_prefix = request.user.profile.product_active_prefix

    if not prefix:
        raise Http404()
    if prefix != user_active_prefix:
        flash(request, 'This product is not in your active prefix', 'danger')
        return redirect(reverse('products:products_list'))

    barcodes = {}
    # for bc in product.barcodes:
    #    barcodes.update({bc.kind: bc})

    if request.GET.get('barcodes'):
        active_tab = 'barcodes'
        barcodes['EAN13'] = True
    elif request.GET.get('cloud'):
        active_tab = 'cloud'
    else:
        active_tab = 'details'

    if prefix.is_upc():
        kind = 'UPCA'
    else:
        kind = 'EAN13'

    template_name = 'products/product_fulledit_form.html'
    context = {          'product': product,
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

            if product.target_market.code != form_data['target_market']:
                gtin_target_market_service.change_target_market(product, form_data['target_market'])

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
            return redirect(reverse('products:products_list'))
        else:
            if product.package_level_id == 70:
                print('ProductForm, errors:', form.errors)
            else:
                print('ProductCaseForm, errors:', form.errors)
    else:  # GET
        form = ProductForm(product)

    context['form'] = form

    target_markets = gtin_target_market_service.get_target_markets_other(product)
    context['target_markets'] = target_markets

    return render(request, template_name, context=context)


@user_agreement_required
def delete_target_market(request, product_id):
    product = Product.service.get_my_product(request.user, product_id)
    target_markets = gtin_target_market_service.get_target_markets_other(product)
    if len(target_markets) <= 0:
        raise Http404()
    gtin_target_market_service.delete_target_market(product, product.target_market)
    product.target_market = target_markets[0].target_market
    product.save()
    url = reverse('products:fulledit', args=(product_id,))
    target_markets_names_arr = []
    for item in target_markets:
        target_markets_names_arr.append(item.target_market.market)
    target_markets_names = ', '.join(target_markets_names_arr)
    flash(request,
          'Product <a href="%s" style="text-decoration:underline">%s</a> exist with %s target markets' %
                                                            (url, product.label_description, target_markets_names),
          'success')
    return redirect(reverse('products:products_list'))


@user_agreement_required
def delete_product(request, product_id):
    product = Product.service.get_my_product(request.user, product_id)
    user_active_prefix = request.user.profile.product_active_prefix
    prefix = prefix_service.find_item(user=request.user, prefix=product.gs1_company_prefix)
    if not prefix:
        raise Http404()
    if prefix != user_active_prefix:
        flash(request, 'This product is not in your active prefix', 'danger')
        return redirect(reverse('products:products_list'))
    if prefix.is_special == 'READ-ONLY':
        flash(request, 'This product belongs to read only range', 'danger')
        return redirect(reverse('products:products_list'))
    #if product.associated_products:
    #    flash(request, 'This product is part of a container and cannot be deleted', 'danger')
    #    return redirect(request.referrer)

    gtin = product.gtin
    if product.image != settings.NO_IMAGE:
        try:
            image = os.path.split(product.image)[1]
        except:
            image = None
    else:
        image = None
    if image:
        delete_product_image(image, request.user.id)

    '''
    barcodes = Barcodes.service.find(product_id=product_id, user_id=request.user.id).all()
    for barcode in barcodes:
        delete_barcode_images(gtin[1:14], current_user.id)
        services.barcode_service.delete(barcode)
    '''

    '''
    sub_product_entries = services.sub_product_service.find(product_id=product_id).all()
    try:
        services.product_service.delete(product)
    except Exception as e:
        logging.getLogger().error('Delete product error: ' + str(e))
        flash('An error happened while trying to delete this product', 'danger')
        return redirect(request.referrer)
    for sbe in sub_product_entries:
        services.sub_product_service.delete(sbe)
    '''

    extra = ''
    if request.GET.get('set'):
        prefix.starting_from = gtin[1:14]
        prefix_service.save(user=request.user, prefix=prefix)
        extra = " Prefix's starting number set to deleted product's GTIN"

    product.delete()
    flash(request, 'Product deleted successfully.' + extra, 'success')

    return redirect(reverse('products:products_list'))


@user_agreement_required
def duplicate_product(request, product_id, target_market):
    product = Product.service.get_my_product(request.user, product_id)
    user_active_prefix = request.user.profile.product_active_prefix
    prefix = prefix_service.find_item(user=request.user, prefix=product.gs1_company_prefix)
    if not prefix:
        raise Http404()
    if prefix != user_active_prefix:
        flash(request, 'This product is not in your active prefix', 'danger')
        return redirect(reverse('products.products_list_js'))
    if prefix.is_special == 'READ-ONLY':
        flash(request, 'This product belongs to read only range', 'danger')
        return redirect(reverse('products.products_list_js'))

    clone_fl = True
    target_markets = gtin_target_market_service.get_target_markets_all(product)
    for item in target_markets:
        if item.target_market.code == target_market:
            clone_fl = False
            break

    # Add new target market
    if clone_fl:
        gtin_target_market_service.add_target_market(product, target_market)
        target_market_record = target_market_service.find_by_code(target_market)
        product.target_market = target_market_record
        product.save()
        return redirect(reverse('products:fulledit', args=(product_id,)))

    # Swap target market form <-> others
    if product.target_market.code != target_market:
        target_market_record = target_market_service.find_by_code(target_market)
        product.target_market = target_market_record
        product.save()
        return redirect(reverse('products:fulledit', args=(product_id,)))

    if not prefix.starting_from:
        flash(request,
              'The next available number is not available or you have exhausted this prefix.'
              ' Product not cloned. To licence an additional company prefix please'
              ' go to the <a href="http://www.gs1ie.organisation/Members-Area">Members Area</a>'
              ' of the GS1 Ireland website.',
              'danger')
        return redirect(reverse('products:fulledit', args=(product_id,)))
    if product.package_level_id != PackageLevel.BASE:
        flash(request, 'You can only clone base unit/each products', 'danger')
        return redirect(reverse('products:fulledit', args=(product_id,)))
    product.id = None
    product.barcodes = []
    product.gtin = product.gtin[0:1] + prefix.starting_from
    product.description = '[CLONED] ' + product.description
    try:
        Product.service.save(product)
    except Exception as e:
        logging.getLogger().error('Product clone error: ' + str(e))
        flash(request, 'AN error occurred while trying to clone this product', 'danger')
        return redirect(reverse('products:fulledit', args=(product_id,)))

    # Update prefix
    try:
        prefix.increment_starting_from()
        prefix_service.save(prefix)
    except Exception as e:
        flash(request, str(e), 'danger')

    product_orig = Product.service.get_my_product(request.user, product_id)
    gtin_target_market_service.clone_product(product_orig, product)

    if request.GET.get('fulledit_js'):
        return redirect(reverse('products:fulledit_js', args=(product.id,)))
    else:
        return redirect(reverse('products:fulledit', args=(product.id,)))
