import json
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings

from BCM.helpers.utils import get_nested_attribute

HEADERS = {'Content-type': 'application/json'}


def _get_cloud_information(user):
    '''
    >>> from django.contrib.auth.models import User
    >>> user = User.objects.create(email='root@root.ru', username='example1234')
    >>> _get_cloud_information(user)
    (None, None, None)
    >>> from BCM.models import Country
    >>> country  = Country.objects.create(name='adsf', slug='ru')
    >>> from member_organisations.models import MemberOrganisation
    >>> member_organisation = MemberOrganisation.objects.create(country=country)
    >>> user.profile.member_organisation = member_organisation
    >>> user.profile.save()
    >>> _get_cloud_information(user)
    ('', '', '')
    '''
    try:
        member_organisation = user.profile.member_organisation
        return (member_organisation.gs1_cloud_username,
                member_organisation.gs1_cloud_secret,
                member_organisation.gs1_cloud_ds_gln)
    except Exception:
        return None, None, None


def _get_key_attributes(user, product):
    """
    >>> from django.contrib.auth.models import User
    >>> user = User.objects.create(email='root@root.ru', username='example432')
    >>> from products.models.product import Product
    >>> from products.models.target_market import TargetMarket
    >>> from products.models.language import Language
    >>> from company_organisations.models import CompanyOrganisation
    >>> from member_organisations.models import MemberOrganisation
    >>> from BCM.models import Country
    >>> country  = Country.objects.create(name='adsf', slug='ru')
    >>> member_organisation = MemberOrganisation.objects.create(country=country)
    >>> company_orgamisation = CompanyOrganisation.objects.create(member_organisation=member_organisation)
    >>> user.profile.company_orgamisation = company_orgamisation
    >>> user.profile.save()
    >>> language = Language.objects.create(slug='ru', name='russian')
    >>> target_market = TargetMarket.objects.create(code='123', market='123')
    >>> product = Product.objects.create(target_market=target_market, language=language)
    >>> data = _get_key_attributes(user, product)
    >>> data['languageCode']
    'ru'
    """

    gs1_cloud_username, gs1_cloud_secret, gs1_cloud_ds_gln = _get_cloud_information(user)

    attributes = {}

    attributes['targetMarket'] = product.target_market.code
    attributes['languageCode'] = product.language.slug
    attributes['companyName'] = getattr(user.profile.company_organisation, 'company', 'NOT SPECIFIED')
    attributes['informationProviderGln'] = gs1_cloud_ds_gln

    # dynamic attributes
    attributes['gtin'] = product.gtin
    attributes['labelDescription'] = product.label_description
    attributes['brand'] = product.brand
    attributes['gpc'] = product.category
    attributes['imageUrlMedium'] = product.website_url

    return attributes


def cloud_add(user, product):
    """
    adds product to GS1 cloud
    :param state:
    :return:
    """
    data = _get_key_attributes(user, product)
    gs1_cloud_username, gs1_cloud_secret, gs1_cloud_ds_gln = _get_cloud_information(user)

    base_url = get_nested_attribute(user, 'profile.member_organisation.gs1_cloud_endpoint')

    response = requests.post(
        f'{base_url}products/',
        data=json.dumps([data]),
        auth=HTTPBasicAuth(gs1_cloud_username, gs1_cloud_secret),
        headers=HEADERS
    )
    return response.json()[0]


def cloud_delete(user, product):
    """
    removes product from GS1 cloud
    :param state:
    :return:
    """
    data = _get_key_attributes(user, product)
    gs1_cloud_username, gs1_cloud_secret, gs1_cloud_ds_gln = _get_cloud_information(user)

    base_url = get_nested_attribute(user, 'profile.member_organisation.gs1_cloud_endpoint')
    response = requests.post(
        f'{base_url}products/delete',
        data=json.dumps([data]),
        auth=HTTPBasicAuth(gs1_cloud_username, gs1_cloud_secret),
        headers=HEADERS
    )
    return response.json()[0]
