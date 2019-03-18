from functools import reduce

__author__ = 'Narayan Kandel'


def resolve_boolean_value(value):
    """
    all value except true or 1 will be treated as False
    :param value:
    :return:
    """
    return_value = False
    if isinstance(value, str):
        v = value.lower()
        if v in ('true', '1'):
            return_value = True

    if isinstance(value, int) and value in [0, 1]:
        return_value = bool(value)
    return return_value


def get_nested_attribute(obj, attr, default_value=None):
    """
    Recurses through an attribute chain to get the ultimate value.
    """

    try:
        return reduce(getattr, attr.split('.'), obj)
    except AttributeError:
        return default_value
