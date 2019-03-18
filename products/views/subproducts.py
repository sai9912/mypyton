import re
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator, InvalidPage

from barcodes.utilities import normalize
from core import flash, jsonify
from services import prefix_service, package_level_service
from services import product_service, sub_product_service
from services import (
    country_of_origin_service,
    target_market_service,
    language_service
)
from services import gtin_target_market_service
from users.helpers import user_agreement_required
from ..forms import FilterForm, SubProductsForm
from ..forms import ProductCaseDetailForm
from ..models.package_level import PackageLevel
from ..models.product import Product
from ..models.sub_product import SubProduct
from ..utilities import upload_image
from ..helpers import product_helper
from ..helpers.product_helper import get_assoc_products_by_products_list


@user_agreement_required
def subproduct_add_case(request):
    """
    Allows for selection of subproducts to be included into
    parent upper level item (PACK, CASE, ...).
    :return:
    """
    session = request.session.get('new_product', {})
    if request.GET.get('gtin', None):
        session['gtin'] = request.GET.get('gtin')
    if request.GET.get('package_level', None):
        session['package_level'] = request.GET.get('package_level')
    if request.GET.get('package_type', None):
        session['package_type'] = request.GET.get('package_type')
    request.session['new_product'] = session

    if not session:
        raise Http404()
    gtin = session.get('gtin', 0)
    prefix = prefix_service.find_item(
        user=request.user,
        starting_from=str(gtin)
    )
    if not prefix:
        raise Http404()
    pl = session.get('package_level', None)
    if not pl:
        flash(request, 'Choose a package level', 'danger')
        return redirect(reverse('products:add_product'))

    try:
        page = int(request.GET.get('page', '1'))
    except (ValueError, TypeError):
        page = 1

    settings_per_page = getattr(settings, 'PRODUCTS_PER_PAGE', 10)
    try:
        per_page = int(request.GET.get('per_page'))
    except (ValueError, TypeError):
        per_page = None
    if per_page:
        session['per_page'] = per_page
    else:
        per_page = session.get('per_page', settings_per_page)

    prefixes = prefix_service.all(user=request.user)
    package_level = package_level_service.get(pl)
    products = Product.service.get_available_subproducts(
        owner=request.user,
        package_level=package_level
    )

    target_markets = gtin_target_market_service.get_by_products_list(products)
    target_market_choices = [['', '']]
    for target_market in target_markets:
        try:
            if target_market_choices[-1][0] == target_market.target_market.code:
                continue
        except Exception:
            pass
        target_market_choices.append([
            target_market.target_market.code,
            target_market.target_market.market
        ])

    filter_data = {}
    form = SubProductsForm()
    filterform = FilterForm()
    if request.method == 'POST':
        form = SubProductsForm(request.POST)
        if form.is_valid():
            if request.POST.get('filtersubmit'):
                filterform = FilterForm(request.POST)
                if filterform.is_valid():
                    products = product_helper.filter_list(products, filterform)
                    session['adding_filter'] = filter_data
            else:
                # form = forms.SubProductsForm(request.form)
                # we no longer use data from form but from session
                sub_products = session.get('sub_products', [])
                sub_products.sort()

                if len(sub_products) > 0:
                    sub_products_data = Product.service.check_subproducts(
                        sub_product_gtins=sub_products,
                        package_level=package_level,
                        owner=request.user
                    )
                    if sub_products_data['is_valid']:
                        # we have subproducts, we move to the next step
                        session['sub_products'] = sub_products
                        # return redirect(reverse('products:subproduct_add_case_details'))
                        return redirect('/products/js-add/#/details?package_level=%s&package_type=%s' % (session['package_level'], session['package_type']))
                    else:
                        # we have incorrect subproducts
                        flash(request, sub_products_data['error'], 'danger')
                        return redirect(reverse('products:subproduct_add_case'))
                else:
                    # we do not have subproducts - we reselect
                    flash(request, 'You must choose products before proceeding to next form', 'danger')
                    return redirect(reverse('products:subproduct_add_case'))
    else:
        session['sub_products'] = []

    if request.GET.get('clear_filter'):
        if session.get('adding_filter'):
            del session['adding_filter']
    if session.get('adding_filter'):
        filter_data = session['adding_filter']
    else:
        filterform = FilterForm()
        filterform.initial['pallet'] = False
        if package_level.id >= PackageLevel.CASE:
            filterform.initial['case'] = False
        if package_level.id >= PackageLevel.PACK:
            filterform.initial['pack'] = False

    # products = ProductFilter(filter_data, queryset=products).qs
    filterform.set_prefixes(prefixes)

    if products:
        paginator = Paginator(products, per_page)
        try:
            paginator_page = paginator.page(page)
        except InvalidPage:
            paginator_page = paginator.page(1)
        object_list = paginator_page.object_list
    else:
        paginator_page = None
        object_list = None

    assoc_products = get_assoc_products_by_products_list(object_list)

    filterform.fields['target_market'].choices = target_market_choices
    filterform.base_fields['target_market'].choices = target_market_choices
    filterform.declared_fields['target_market'].choices = target_market_choices
    context = {
        'products': object_list,
        'assoc_products': assoc_products,
        'prefix': prefix,
        'form': form,
        'filterform': filterform,
        'pagination': paginator_page,
        'per_page': per_page,
        'ppp': settings_per_page,
        'enable_leading': True     # user.profile.enable_leading
    }

    return render(request, 'products/subproduct_add_case.html', context=context)


@user_agreement_required
def subproduct_add_case_skip(request):
    """
    Clean selection of subproducts to be included into parent
    upper level item (PACK, CASE, ...).
    :return:
    """
    session = request.session.get('new_product', {})
    if not session:
        raise Http404()

    gtin = session.get('gtin', 0)
    prefix = prefix_service.find_item(user=request.user, starting_from=str(gtin))
    if not prefix:
        raise Http404()

    pl = session.get('package_level', None)
    if not pl:
        flash(request, 'Choose a package level', 'danger')
        return redirect(reverse('products:add_product'))

    # we remove subproducts, we move to the next step
    session['sub_products'] = []
    return redirect('/products/js-add/#/details?package_level=%s&package_type=%s' % (session['package_level'], session['package_type']))



@user_agreement_required
def subproduct_add_case_edit(request):
    """
    Allows for selection of subproducts to be included into parent
    upper level item (PACK, CASE, ...).
    :return:
    """
    session = request.session.get('new_product', {})
    if request.GET.get('gtin', None):
        session['gtin'] = request.GET.get('gtin')
    if request.GET.get('package_level', None):
        session['package_level'] = request.GET.get('package_level')
    else:
        session['package_level'] = 30
    if request.GET.get('package_type', None):
        session['package_type'] = request.GET.get('package_type')
    request.session['new_product'] = session

    if not session:
        raise Http404()
    gtin = session.get('gtin', None)
    if not gtin:
        return redirect(reverse('products:products_list'))
    # prefix = prefix_service.find_item(
    #       user=request.user,
    #       starting_from=str(gtin)
    # )
    # if not prefix:
    #    raise Http404()
    # pl = session.get('package_level', None)
    # if not pl:
    #    flash(request, 'Choose a package level', 'danger')
    #    return redirect(reverse('products:add_product'))

    try:
        page = int(request.GET.get('page', '1'))
    except (ValueError, TypeError):
        page = 1

    settings_per_page = getattr(settings, 'PRODUCTS_PER_PAGE', 10)

    try:
        per_page = int(request.GET.get('per_page'))
    except (ValueError, TypeError):
        per_page = None
    if per_page:
        session['per_page'] = per_page
    else:
        per_page = session.get('per_page', settings_per_page)

    prefixes = prefix_service.all(user=request.user)
    pl = session['package_level']

    package_level = package_level_service.get(pl)
    products = Product.service.get_available_subproducts(
        owner=request.user,
        package_level=package_level
    )

    target_markets = gtin_target_market_service.get_by_products_list(products)
    target_market_choices = [['', '']]
    for target_market in target_markets:
        try:
            if target_market_choices[-1][0] == target_market.target_market.code:
                continue
        except Exception:
            pass
        target_market_choices.append([target_market.target_market.code, target_market.target_market.market])

    filter_data = {}
    form = SubProductsForm()
    filterform = FilterForm()
    if request.method == 'POST':
        form = SubProductsForm(request.POST)
        if form.is_valid():
            if request.POST.get('filtersubmit'):
                filterform = FilterForm(request.POST)
                if filterform.is_valid():
                    products = product_helper.filter_list(products, filterform)
                    session['adding_filter'] = filter_data
            else:
                # form = forms.SubProductsForm(request.form)
                # we no longer use data from form but from session
                sub_products = session.get('sub_products', [])

                sub_products_data = Product.service.check_subproducts(
                    sub_product_gtins=sub_products,
                    owner=request.user,
                    package_level=package_level
                )
                if not sub_products_data['is_valid']:
                    flash(request, sub_products_data['error'], 'danger')
                else:
                    try:
                        product = Product.objects.get(gtin=gtin)
                    except:
                        return redirect(reverse('products:products_list'))

                    for sub_product_gtin in sub_products:
                        try:
                            sub_product = Product.objects.get(gtin=sub_product_gtin)
                        except:
                            continue

                        SubProduct.objects.get_or_create(
                            product=product,
                            sub_product=sub_product,
                            defaults=dict(quantity=1)
                        )

                    edit_url = reverse('products:fulledit_js', args=(product.id,))
                    return redirect(edit_url)
    else:
        session['sub_products'] = []

    if request.GET.get('clear_filter'):
        if session.get('adding_filter'):
            del session['adding_filter']
    if session.get('adding_filter'):
        filter_data = session['adding_filter']
    else:
        filterform = FilterForm()
        filterform.initial['pallet'] = False
        #if package_level.id >= PackageLevel.CASE:
        #    filterform.initial['case'] = False
        #if package_level.id >= PackageLevel.PACK:
        #    filterform.initial['pack'] = False

    # products = ProductFilter(filter_data, queryset=products).qs
    filterform.set_prefixes(prefixes)

    if products:
        paginator = Paginator(products, per_page)
        try:
            paginator_page = paginator.page(page)
        except InvalidPage:
            paginator_page = paginator.page(1)
        object_list = paginator_page.object_list
    else:
        paginator_page = None
        object_list = None

    assoc_products = get_assoc_products_by_products_list(object_list)

    filterform.fields['target_market'].choices = target_market_choices
    filterform.base_fields['target_market'].choices = target_market_choices
    filterform.declared_fields['target_market'].choices = target_market_choices
    context = {'products': object_list,
         'assoc_products': assoc_products,
                   'form': form,
             'filterform': filterform,
             'pagination': paginator_page,
               'per_page': per_page,
                    'ppp': settings_per_page,
         'enable_leading': True  # user.profile.enable_leading
    }

    return render(request, 'products/subproduct_add_case_edit.html', context=context)


@user_agreement_required
def subproduct_add_case_edit_skip(request):
    """
    Clean selection of subproducts to be included into parent upper level item (PACK, CASE, ...).
    :return:
    """
    session = request.session.get('new_product', {})
    if not session:
        raise Http404()

    gtin = session.get('gtin', 0)
    try:
        product = Product.objects.get(gtin=gtin)
    except:
        return redirect(reverse('products:products_list'))

    # we remove subproducts, we move to the next step
    session['sub_products'] = []
    return redirect(reverse('products:fulledit_js', args=(product.id,)))


def _get_prods_from_form(request):
    sub_prods = []
    for k in list(request.POST):
        v = request.POST[k]
        if 'pid_' in k:
            pid = k.split('_')[1]
            sub_product = product_service.get(id=pid)
            valid = False
            try:
                int(v)
                valid = True
            except (ValueError, TypeError):
                pass
            sub_prods.append((sub_product, v, valid))
    return sub_prods


def _validate_subprods(request, sub_prods):
    # validate quantity of subproducts
    _total_count = 0
    _subs_valid = True
    for k, v, _valid in sub_prods:
        try:
            _total_count += int(v)
        except:
            flash(request, 'subproduct %s - invalid quantity' % k.gtin, 'danger')
            _subs_valid = False

    if not _total_count:
        flash(request, 'Total count of subproducts must be bigger than 0 (error #009)', 'danger')
        _subs_valid = False

    return _subs_valid


@user_agreement_required
def subproduct_add_case_details(request):
    """
    GET / POST for adding a new upper level item (case, pack, pallet)
    :template_name: products/product_details_form.html
    :return:
    """
    session = request.session.get('new_product', None)
    if not session:
        raise Http404()

    # Check session and restart if missing, allow for missing sub_products
    for k in ['sub_products', 'package_level', 'gtin']:

        if k not in session.keys():
            del session['new_product']
            flash(request, 'Add new product restarted #011', 'danger')
            return redirect(reverse('products:add_product'))
    gtin = session.get('gtin', '0')

    prefix = None

    if len(gtin) == 13:
        prefix = prefix_service.find_item(
            user=request.user,
            starting_from=str(gtin)
        )
    elif len(gtin) == 14:  # FIXME - dirty hack
        p_list = [gtin[1:x] for x in range(-6, 0)]  # build a list of possible prefixes
        prefix = prefix_service.find_prefix_from_list(p_list)  # select the correct one

    if not prefix:
        raise Http404()
    if prefix.is_upc():
        kind = 'UPCA'
    else:
        kind = 'EAN13'

    p_ids = session.get('sub_products', [])

    if not p_ids:
        flash(request, 'Choose products for this container', 'danger')
        return redirect(reverse('products:subproduct_add_case'))

    if len(p_ids) == 1 and p_ids[0] == '0':
        arbitrary = True
        products = []
    elif len(p_ids) == 0:
        arbitrary = False
        products = []
    else:
        arbitrary = False
        products = [
            (p, 0, True)
            for p in Product.objects.filter(id__in=p_ids).order_by('gtin').all()
        ]
        if len(products) == 0:
            flash(request, 'Choose products for this container', 'danger')
            return redirect(reverse('products:subproduct_add_case'))

    title = 'New item (Step 2 of 2: Details)'

    readonly = False
    # if not request.user.enable_leading:
    #     readonly = True

    context = {'prefix': prefix,
               'sub_products': products,
               'title': title,
               'arbitrary': arbitrary,
               'product_package_level_id': int(session.get('package_level', '0')),
               'kind': kind,
               'readonly': readonly}

    if len(gtin) == 13:
        context.update({'gtin0': '0',
                        'gtin13': session.get('gtin','')})
    elif len(gtin) == 14:
        # readonly = False
        context.update({'gtin0': gtin[0],
                        'gtin13': gtin[1:]})

    context['leading_gln'] = normalize('EAN13', prefix.prefix)

    if request.method == 'POST':
        context['is_new'] = 0

        sub_prods = _get_prods_from_form(request)
        context['sub_products'] = sub_prods

        form = ProductCaseDetailForm(request.POST)

        form_valid = form.is_valid(show_flash=request)
        if not form_valid:
            for error in form.errors:
                if error != 'optionalFields':
                    error_message = '%s: %s' % (error, form.errors[error][0])
                    flash(request, error_message, 'danger')

        if not sub_prods and not arbitrary:
            flash(request, 'You must enter the number of products contained (error #006)', 'danger')
            form_valid = False

        if not arbitrary:
            subs_valid = _validate_subprods(request, sub_prods)
        else:
            subs_valid = True

        if not subs_valid:
            form.errors['subProducts'] = ['invalid subproducts']

        if form.data.get('gtin', '')[1:14].startswith(prefix.prefix):
            gtin_valid = True
        else:
            flash(request, 'You entered a non valid GTIN number (error #001)', 'danger')
            gtin_valid = False

        if form_valid and subs_valid and gtin_valid:
            form_data = {}
            for formfield in form.data:
                try:
                    if formfield == 'csrfmiddlewaretoken':
                        continue
                    if form.data[formfield] != '':
                        form_data[formfield] = form.data[formfield]
                    else:
                        pass
                except Exception:
                    pass

            try:
                ### PRODUCT CREATE UI (PACK)
                product = Product.service.create(owner=request.user,
                                                 company_organisation=prefix.company_organisation,
                                                 prefix=prefix,
                                                 **form_data)
            except Exception as e:
                flash(request, str(e), 'danger')
                return redirect(reverse('products:subproduct_add_case_details'))

            # Load image
            if request.FILES:
                upload_image(request, product)

            # Update prefix
            try:
                prefix.increment_starting_from()
                prefix_service.save(prefix)
            except Exception as e:
                flash(request, str(e), 'danger')

            if not arbitrary:
                for sub_p in sub_prods:
                    quantity = int(sub_p[1])
                    if quantity > 0:
                        sub_product_service.create(product_id=product.id,
                                                   sub_product_id=sub_p[0].id,
                                                   quantity=sub_p[1])

            if request.session.get('new_product'):
                del request.session['new_product']

            return redirect(reverse('products:view_product_summary', args=(product.id,)))
    else:  # GET
        context['is_new'] = 1
        form = ProductCaseDetailForm()
        #_add_field_descriptions(form)
        if len(products) > 0:
            form.initial['brand'] = products[0][0].brand
            form.initial['sub_brand'] = products[0][0].sub_brand
            form.initial['functional_name'] = products[0][0].functional_name
            form.initial['variant'] = products[0][0].variant
            # copy category from child if there is just one child (issue #147)
            form.initial['category'] = products[0][0].category
        # set default GLN
        form.initial['gln_of_information_provider'] = normalize('EAN13', prefix.prefix)
    form.initial['company'] = prefix.company_organisation.company
    form.initial['package_level'] = session.get('package_level', '0')
    form.initial['package_type'] = session.get('package_type', '0')
    form.initial['image'] = session.get('image', settings.NO_IMAGE)

    # if _session['package_level'] in ["4", "70"]:
    #    form.bar_placement.data = settings.STATIC_URL + 'products/site/wizard/proddesc/base.gif'
    if session.get('package_level', '0') in ['3', '60']:
        form.initial['bar_placement'] = settings.STATIC_URL + 'products/site/wizard/proddesc/innerpack_PIDS.gif'
    elif session.get('package_level', '0') in ['2', '50']:
        form.initial['bar_placement'] = settings.STATIC_URL + 'products/site/wizard/proddesc/case.png'
    elif session['package_level'] in ['1', '30']:
        form.initial['bar_placement'] = settings.STATIC_URL + 'products/site/wizard/proddesc/pallet_PIDS.gif'

    context['form'] = form

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

    return render(request,
                  'products/product_details_form.html',
                  context=context)


@user_agreement_required
def subproduct_ajax_select(request, product_id):
    """
    makes sub-product selected
    """
    product = Product.service.get_my_product(request.user, product_id)
    if not request.session.get('new_product', None):
        request.session['new_product'] = {}
    if not request.session['new_product'].get('sub_products'):
        request.session['new_product']['sub_products'] = []
    if product.id not in request.session['new_product']['sub_products']:
        request.session['new_product']['sub_products'].append(product.gtin)
    return jsonify(success=True)


@user_agreement_required
def subproduct_ajax_unselect(request, product_id):
    """
    makes sub-product un-selected
    """
    product = Product.service.get_my_product(request.user, product_id)
    if not request.session.get('new_product', None):
        request.session['new_product'] = {}
    if not request.session['new_product'].get('sub_products'):
        request.session['new_product']['sub_products'] = []
    if product.id in request.session['new_product']['sub_products']:
        request.session['new_product']['sub_products'].remove(product.gtin)
    return jsonify(success=True)


@user_agreement_required
def subproduct_ajax_selected(request):
    """
    returns selected subproducts
    """
    try:
        sub_products = request.session['new_product'].get('sub_products', [])
        sub_products.sort()
    except:
        sub_products = []
    return jsonify(sub_products=sub_products)


@user_agreement_required
def add_product_select_arbitrary(request):
    """
    starts arbitrary (CASE or PACK) creation with no subproducts
    :return:
    """
    '''
    _session = session.get('new_product', None)
    if not _session:
        abort(404)
    gtin = _session['gtin']
    prefix = services.prefix_service.find_item(starting_from=str(gtin))
    if not prefix:
        abort(404)
    pl = _session.get('package_level', None)
    if not pl:
        flash('Choose a package level', 'danger')
        return redirect(url_for('products.add_product'))
    session['new_product']['sub_products'] = ["0"]
    if session['new_product'].get('express'):
        return redirect(url_for('products.add_product_case_express'))
    else:
        return redirect(url_for('products.add_product_case_details'))
    '''
    return HttpResponse('products:add_product_select_arbitrary')

@user_agreement_required
def ajax_av_subproducts_list(request, product_id):
    """
    Given a product's ID retrieve all related subproducts and quantities
    :param key:
    :return:
    """
    product = Product.service.get_my_product(request.user, product_id)
    all_in_range = Product.service.get_available_subproducts(
        owner=request.user,
        package_level=product.package_level
    )
    return jsonify(data=[
        {
            'DT_RowId': product.id,
            'gtin': product.gtin,
            'package_level': product.package_level.unit_descriptor,
            'description': product.description
        } for product in all_in_range
    ])


@user_agreement_required
def ajax_subproducts_list(request, product_id):
    """
    Given a product's ID retrieve all related subproducts and quantities
    :param key:
    :return:
    """
    product = Product.service.get_my_product(request.user, product_id)
    data = [{
        'DT_RowId': subproduct.sub_product.id,
        'gtin': subproduct.sub_product.gtin,
        'package_level': subproduct.sub_product.package_level.unit_descriptor,
        'description': subproduct.sub_product.description,
        'quantity': subproduct.quantity,
    } for subproduct in sub_product_service.get_associated(product)
    ]

    return jsonify(data=data)


def _get_request_quantity(dict_):
    """
    retrieves quantity submitted in request
    :param dict:
    :return:
    """
    rx = re.compile('data\[(\d+)\]\[quantity\]')
    for key, value in dict_.items():
        m = rx.match(key)
        if m:
            return int(m.group(1)), int(value)
    return False, False


@user_agreement_required
def ajax_subproduct_edit(request, product_id):
    subproduct_id, quantity = _get_request_quantity(request.POST)
    action = request.POST.get('action', None)
    if action == 'remove':
        res = sub_product_service.delete_id(
            request.user,
            product_id,
            subproduct_id
        )
        if not res:
            return jsonify(status='Error', message='Subproduct not found')
    elif action == 'edit':
        subproduct, created = sub_product_service.get_or_create_id(
            request.user,
            product_id,
            subproduct_id
        )
        if not subproduct:
            return jsonify(status='Error', message='Subproduct not found')
        subproduct.quantity = quantity
        subproduct.save()
    else:
        return jsonify(status='Error', message='Unknown command')
    return jsonify(status='Ok')


@user_agreement_required
def ajax_subproduct_add(request, product_id):
    subproduct_id, quantity = _get_request_quantity(request.POST)
    action = request.POST.get('action', None)
    if action == 'edit':
        subproduct, created = sub_product_service.get_or_create_id(
            request.user,
            product_id,
            subproduct_id
        )
        if not subproduct:
            return jsonify(status='Error', message='Subproduct not found')
        subproduct.quantity += quantity
        subproduct.save()
    else:
        return jsonify(status='Error', message='Unknown command')
    return jsonify(status='Ok')
