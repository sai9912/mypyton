import logging
import os

from django.http import Http404
from django.shortcuts import render, redirect, reverse

from core import flash
from services import prefix_service
from users.helpers import user_agreement_required
from products.models.product import Product

@user_agreement_required
def fulledit(request, product_id):
    """
    displays via GET and provides product update mechanics via POST
    :param product_id:
    :return:
    """
    product = Product.service.get_my_product(request.user, product_id)
    user_active_prefix = request.user.profile.product_active_prefix
    prefix = prefix_service.find_item(user=request.user, prefix=product.gs1_company_prefix)
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
    elif request.GET.get('cloud'):
        active_tab = 'cloud'
    else:
        active_tab = 'details'

    if prefix.is_upc():
        kind = 'UPCA'
    else:
        kind = 'EAN13'

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

    # if sub_products:
    #    context.update({'nop': product.number_of_products()})

    # context['sub_products'] = _get_subprods_from_obj(product)

    return render(request, 'products_react/product_react_fulledit_form.html', context=context)
