from products.models.product import Product


def get_range_data(request):
    from services import prefix_service
    prefix = prefix_service.find(user=request.user).first()
    if not prefix:
        return ''
    if prefix.is_upc():
        prfx = prefix.prefix[1:]
    else:
        prfx = prefix.prefix

    products = Product.service.filter(owner=request.user, gs1_company_prefix=prefix.prefix).all()
    prfxs = prefix.get_available_gtins(products, True)

    #locations = location_service.find(owner=user, gs1_company_prefix=prefix.prefix).all()
    locations = []
    prfxs2 = prefix.get_available_glns(locations, True)

    return prfx, len(products), prfxs, len(locations), prfxs2
