from django import template

register = template.Library()


@register.filter
def mul(value,arg):
    try:
        return value * arg
    except:
        return ''


@register.simple_tag
def get_localized_product_field(product, field_name):
    """
    returns localized field value by a product language
    """

    if product.language:
        return getattr(product, f'{field_name}_{product.language.slug}', None)
    else:
        return getattr(product, field_name, None)
