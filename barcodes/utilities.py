import logging
import trml2pdf
import hashlib
import os

from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.staticfiles.templatetags.staticfiles import static

from products.forms import ProductForm
from products.models.product import Product


def isValid(nums):
    ''' Returns boolean indicating if check digit is correctly calculated using mod 10 algorithm.
    >>> isValid('')
    False
    >>> isValid('012345678901')
    False
    >>> isValid('012345678905')
    True
    '''
    if not nums: return False
    cd1 = nums[-1]
    meat = nums[0:-1][::-1]  # cut cd away, reverse string, since x3 always applays from right (BC)
    odds = sum(map(lambda i: int(i) * 3, list(meat[0::2])))
    evns = sum(map(lambda i: int(i), list(meat[1::2])))
    cd2 = str(10 - ((odds + evns) % 10))[-1]  # 0 if 10 or reminder
    return cd1 == cd2


def from_14d(bc, type):
    '''
    >>> from_14d('12345678911234', type='UPCA')
    '345678911234'
    '''
    if len(bc) == 14:
        bc = bc[1:]
        if type == 'UPCA':
            bc = bc[1:]
    return bc


def to_14d(bc, type):
    '''
    >>> to_14d('345678911234', type='UPCA')
    '00345678911234'
    '''
    if len(bc) < 14:
        bc = "0" + bc
        if type == "UPCA":
            bc = "0" + bc
    return bc


def prev_next(bc, prefix):
    '''
    >>> prev_next('12345678911234', prefix='12')
    ('1234567891125', '1234567891125')

    >>> prev_next('12000000000009', prefix='12')
    (None, '1200000000003')

    >>> prev_next('99999999999994', prefix='99')
    ('9999999999994', None)
    '''
    bc = bc[:-1]
    serial = bc[len(prefix):]
    prev_bc = int(serial) - 1
    if prev_bc < 0:
        prev_bc = None
    else:
        f = '{0:0%d}' % len(serial)
        prev_bc = normalize('EAN13', prefix + f.format(prev_bc))
    next_bc = int(serial) + 1
    if len(str(next_bc)) > len(serial):
        next_bc = None
    else:
        f = '{0:0%d}' % len(serial)
        next_bc = normalize('EAN13', prefix + f.format(next_bc))
    return prev_bc, next_bc


def normalize(kind, value):
    ''' Normalizes EAN/UPC to required length
    >>> normalize('UPCA','123')
    '123000000006'
    >>> normalize('EAN13','123')
    '1230000000000'
    >>> normalize('ISBN13','123')
    '9781230000008'
    >>> normalize('ISBN13','978123')
    '9781230000008'
    >>> normalize('GTIN14','978123')
    '97812300000002'
    >>> try:
    ...     normalize('Gtin14','978123')
    ... except Exception as e:
    ...     e
    Exception('wrong kind!',)
    '''
    if kind == "UPCA":
        value1 = ''.join(list(filter(lambda x: x.isdigit(), value)))
        value2 = '{0:0<12}'.format(value1)[0:12]
        value3 = getValid(value2)
        return value3
    if kind == "EAN13":
        value1 = ''.join(list(filter(lambda x: x.isdigit(), value)))
        value2 = '{0:0<13}'.format(value1)[0:13]
        value3 = getValid(value2)
        return value3
    if kind == "ISBN13":
        value1 = ''.join(list(filter(lambda x: x.isdigit(), value)))
        if value1.find('978') == 0:
            value2 = value1
        else:
            value2 = "978%s" % value1
        value3 = '{0:0<13}'.format(value2)[0:13]
        value4 = getValid(value3)
        return value4
    if kind == "GTIN14":
        value1 = ''.join(list(filter(lambda x: x.isdigit(), value)))
        value2 = '{0:0<14}'.format(value1)[0:14]
        value3 = getValid(value2)
        return value3
    raise Exception("wrong kind!")


def getValid(nums):
    ''' Fixes incorrect number replacing the CD with the corrected one.
    >>> getValid('012345678901')
    '012345678905'
    '''
    if not nums: return None
    cd1 = nums[-1]
    meat = nums[0:-1][::-1]  # cut cd away, reverse string, since x3 always applays from right (BC)
    odds = sum(map(lambda i: int(i) * 3, list(meat[0::2])))
    evns = sum(map(lambda i: int(i), list(meat[1::2])))
    cd2 = str(10 - ((odds + evns) % 10))[-1]  # 0 if 10 or reminder
    return nums[0:-1] + cd2


def make_omlet(b):
    """ Hashes up vital barcode params and presents the as a hash
    """
    s = ''.join([str(i) for i in [b.gtin, b.kind, b.size, b.bwr, b.rqz, b.pmk, b.price, b.name, b.debug]])
    return hashlib.sha1(s.encode()).hexdigest()[0:5]


def get_barcode_type(gtin, package_level_id):
    """
    Calculates barcode type
    actually Product model has bar_type attribute,
    but it seems it doesn't reflect an actual status
    """

    # ALLOWED_BARCODE_TYPES = ['EAN13', 'ITF14', 'UPCA']
    if gtin and package_level_id:
        gtin13 = gtin[1:14]
        if 40 <= package_level_id <= 70:
            if package_level_id == 70:
                if gtin13.startswith('0'):
                    return 'UPCA'
                else:
                    return 'EAN13'
            else:
                return 'ITF14'
    return None


# def get_spam(l):
#     """
#     >>> get_spam({'a':1,'b':'foo'})
#     'acbd1'
#     """
#     s = ''
#     for item in l.values():
#         if type(item) in [str,float,list]:
#              s += str(item)
#     hash = md5.new()
#     hash.update(s)
#     value = hash.hexdigest()[0:5]
#     return value


def check_dir(s):
    media_root = '/tmp'  # FIXME
    d = '%s/%s' % (media_root, s)
    logging.getLogger().debug("will check %s" % d)
    if not os.path.exists(d):
        logging.getLogger().debug("will generate %s" % d)
        os.makedirs(d)
    else:
        logging.getLogger().debug("directory %s exists -- do nothing" % d)
    return d


class Storage(dict):
    """
    A Storage object is like a dictionary except `obj.foo` can be used
    in addition to `obj['foo']`.

        >>> o = Storage(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> o
        <Storage {'a': 2}>
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'
        >>> del o.z
        Traceback (most recent call last):
            ...
        AttributeError: 'z'


    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __repr__(self):
        return '<Storage ' + dict.__repr__(self) + '>'


def storify(mapping, *requireds, **defaults):
    """
    Creates a `storage` object from dictionary `mapping`, raising `KeyError` if
    d doesn't have all of the keys in `requireds` and using the default
    values for keys found in `defaults`.

    For example, `storify({'a':1, 'c':3}, b=2, c=0)` will return the equivalent of
    `storage({'a':1, 'b':2, 'c':3})`.

    If a `storify` value is a list (e.g. multiple values in a form submission),
    `storify` returns the last element of the list, unless the key appears in
    `defaults` as a list. Thus:

        >>> storify({'a': [1, 2]}).a
        2
        >>> storify({'a': [1, 2]}, a=[]).a
        [1, 2]
        >>> storify({'a':1}, a=[]).a
        [1]
        >>> storify({}, a=[]).a
        []

    Similarly, if the value has a `value` attribute, `storify will return _its_
    value, unless the key appears in `defaults` as a dictionary.

        >>> storify({'a': Storage(value=1)}).a
        1
        >>> storify({'a': Storage(value=1)}, a={}).a
        <Storage {'value': 1}>
        >>> storify({}, a={}).a
        {}

    """

    def getvalue(x):
        if hasattr(x, 'value'):
            return x.value
        else:
            return x

    stor = Storage()
    for key in requireds + tuple(mapping.keys()):
        value = mapping[key]
        if isinstance(value, list):
            if isinstance(defaults.get(key), list):
                value = [getvalue(x) for x in value]
            else:
                value = value[-1]
        if not isinstance(defaults.get(key), dict):
            value = getvalue(value)
        if isinstance(defaults.get(key), list) and not isinstance(value, list):
            value = [value]
        setattr(stor, key, value)

    for (key, value) in defaults.items():
        result = value
        if hasattr(stor, key):
            result = stor[key]
        if value == () and not isinstance(result, tuple):
            result = (result,)  # pragma: no cover
        setattr(stor, key, result)

    return stor


def get_completion(current_user, gtin):
    """indicates if user has all the master data to generate the barcode
    >>> from django.contrib.auth.models import User
    >>> gtin = '1111'
    >>> user = User.objects.create(email='example@root.ru', username='root124')
    >>> get_completion(user, gtin=gtin)
    False
    >>> Product.objects.create(owner=user, gtin=gtin)
    <Product: Product object (1)>
    >>> get_completion(user, gtin=gtin)
    False
    """
    try:
        product = Product.service.filter(owner=current_user, gtin=gtin).first()
        form = ProductForm(product)
        res = form.is_valid(show_flash=False)
    except Exception as e:
        res = False
    return res


def generate_download_file(parameters):
    from barcodes.generator import get_payload
    from barcodes.barcode import Barcode
    from barcodes.models import label_service
    from barcodes.views import ALLOWED_BARCODE_TYPES

    bc_kind = parameters.get('bc_kind')
    gtin = parameters.get('gtin')
    dl_type = parameters.get('dl_type')

    if bc_kind not in ALLOWED_BARCODE_TYPES:
        return {'success': False, 'msg': 'Wrong barcode kind'}

    kind = bc_kind

    if kind == 'EAN13':
        gtin = gtin[1:14]
    try:
        size = float(parameters.get('size', '1.0'))
    except:
        size = 1.0
    try:
        bwr = float(parameters.get('bwr', '0.0'))
    except:
        bwr = 0.0

    rqz = parameters.get('rqz')
    marks = parameters.get('marks')
    debug = parameters.get('debug')
    meta_barcode = Barcode(gtin)
    static_path = os.path.join(settings.BARCODES_FILES_PATH, str(parameters.get('user_id')), kind)
    if dl_type == 'raster':
        file_type = parameters.get('file_type', 'png')
        resolution = parameters.get('resolution', '300 dpi').split(' ')[0]
        fln = get_payload(meta_barcode, kind, file_type,
                          resolution=resolution,
                          static_path=static_path,
                          debug=debug,
                          marks=marks,
                          scale=size,
                          rqz=rqz,
                          bwr=bwr)
    elif dl_type == 'ps':
        ps_type = parameters.get('ps_type', 'win')
        if ps_type == 'mac':
            fln = get_payload(meta_barcode, kind, 'eps_Mac',
                              static_path=static_path,
                              debug=debug, marks=marks,
                              scale=size, rqz=rqz, bwr=bwr)
        else:
            fln = get_payload(meta_barcode, kind, 'eps_PC',
                              static_path=static_path,
                              debug=debug, marks=marks,
                              scale=size, rqz=rqz, bwr=bwr)
    elif dl_type == 'label':
        file_type = 'jpg'
        resolution = '600'
        label_type = parameters.get('label_type', 'L7161')
        fln = get_payload(meta_barcode, kind, file_type,
                          resolution=resolution,
                          static_path=static_path,
                          debug=debug,
                          marks=marks, scale=size, rqz=rqz, bwr=bwr)
        from PIL import Image

        bc_image = Image.open(fln)
        label = label_service.first(code=label_type)
        if label is None:
            return {'success': False, 'msg': 'Error in your request'}
        img_ratio = float(bc_image.size[0]) / float(bc_image.size[1])
        if img_ratio < label.ratio:
            label_height_val = label.height
            label_width = "{0:.2f}".format(label_height_val * img_ratio)
            label_height = "{0:.2f}".format(label.height)
        else:
            label_width_val = label.width
            label_height = "{0:.2f}".format(label_width_val / img_ratio)
            label_width = "{0:.2f}".format(label.width)

        context = {
            'range_rows': range(label.rows),
            'range_cols': range(label.cols),
            'has_gap': label.has_gap,
            'label_width': label_width,
            'label_height': label_height,
            'image': fln
        }

        pdf = render_to_string(label.template, context)  # request is None here
        pdf_lines = pdf.split('\n')
        pdf_lines_nonempty = [line for line in pdf_lines if line.strip() != '']
        pdf_nonempty = '\n'.join(pdf_lines_nonempty)
        try:
            pdf_parsed = trml2pdf.parseString(pdf_nonempty)
        except Exception as e:
            print(e)
            return {'success': False, 'msg': 'Error in your request'}

        # save pdf as file to handle all file types in one place
        fln = os.path.join(static_path, f'{gtin}.pdf')
        with open(fln, 'wb') as f:
            f.write(pdf_parsed)
    else:
        return {'success': False, 'msg': 'Error in your request'}

    file_name = fln.split('/')[-1]
    static_url = os.path.join(
        settings.BARCODES_URL, str(parameters.get('user_id')), kind, file_name
    )
    static_url = static(static_url)

    return {
        'success': True,
        'file_path': fln,
        'static_file_path': static_url,
    }
