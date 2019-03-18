import requests
from django.utils.translation import activate
from requests.auth import HTTPBasicAuth
from rq.decorators import job
import django_rq

from BCM.helpers.utils import get_nested_attribute
from audit.models import CloudLog
from products.helpers.product_helper import prepare_instance_data, gs1_fields_changed

rq_connection = django_rq.get_connection()
rq_queue = django_rq.get_queue()

# Code identifying the result of the operation
GS1_RESPONSE_STATUS = {
    1: 'Product record created',
    2: 'Product record modified',
    3: 'Product record refreshed',
    4: 'Product record deleted',
    5: 'Operation failed',
    6: 'Not authorized to perform this operation',
    7: 'Key is unknown',
    8: 'Key is active',
    9: 'Key is inactive',
}


def log_gs1_response(user, instance, response_json):
    """
    format and log gs1 response to the django log model
    """

    if response_json.get('response_text'):
        gs1_message = response_json['response_text']
    elif response_json.get('reason'):
        gs1_message = ', '.join([
            f'{record["path"]} : {record["message"]}'
            for record in response_json['reason']
        ])
    else:
        gs1_message = '--'

    CloudLog.service.log(
        user=user,
        key=instance.gtin,
        gs1_cloud_last_rc=gs1_message,
        msg=GS1_RESPONSE_STATUS[response_json['status']],
        ref='--',
    )


@job(rq_queue, timeout=60 * 3, ttl=60 * 30, result_ttl=60 * 60 * 24)
def update_gs1_cloud_product(instance, original_instance, user, force=False):
    """
    timeout - when this parameter is exceeded task will be finished with JobTimeoutException
    ttl - specifies the maximum queued time of the job before it’ll be cancelled
    result_ttl - result will be kept for the given period
    """

    from products.models.product import Product

    gs1_username = instance.member_organisation.gs1_cloud_username

    gs1_password = instance.member_organisation.gs1_cloud_secret

    gs1_cloud_endpoint = instance.member_organisation.gs1_cloud_endpoint

    gs1_data_source_gln = instance.member_organisation.gs1_cloud_ds_gln

    company_name = instance.company_organisation.name or instance.company_organisation.company

    gs1_products_api_url = f'{gs1_cloud_endpoint}products/'

    fields_map = {
        'gtin': 'gtin',
        'targetMarket': 'target_market.code',
        'brand': 'brand',  # i18n allowed
        'labelDescription': 'label_description',  # i18n allowed
        'companyName': 'company_organisation.name',  # i18n allowed
        'gpc': 'category',
        'imageUrlMedium': 'image',  # i18n allowed
        'informationProviderGln': 'gln_of_information_provider',
    }

    if instance.language:
        activate(instance.language.slug)

    session = requests.Session()
    session.auth = HTTPBasicAuth(gs1_username, gs1_password)
    response = None

    post_data = prepare_instance_data(fields_map, instance)
    post_data['dataSourceGln'] = gs1_data_source_gln

    # temp. fix for company_name that needs to be translated in the cloud but is not translated in the app
    try:
        post_data['companyName'][0]['value'] = company_name
    except Exception as e:
        print(e)

    # temp. fix to fully-qualify hosted image
    try:
        # skip externally hosted images
        if post_data['imageUrlMedium'][0]['value'].find('http') == 0:
            pass
        else:
            # build fqn based on the environment
            if gs1_products_api_url.find('stg') != -1:  # staging
                post_data['imageUrlMedium'][0]['value'] = \
                    f"https://activate.stg.gs1.org{post_data['imageUrlMedium'][0]['value']}"
            else:   # production
                post_data['imageUrlMedium'][0]['value'] = \
                    f"https://activate.gs1.org{post_data['imageUrlMedium'][0]['value']}"
    except Exception as e:
        print(e)

    is_upload_required = gs1_fields_changed(fields_map, instance, original_instance)

    response_json = None

    # force override uploding if specified
    is_upload_required = is_upload_required or force

    if instance.gs1_cloud_state == 'ACTIVE' and is_upload_required:
        # ADD(new instance) or UPDATE (an existing instance) to gs1 cloud
        if original_instance and original_instance.pk:
            # UPDATE
            api_url = f'{gs1_products_api_url}/{instance.gtin}/{instance.target_market.code}'
            print("CLOUD UPDATE:", post_data)
            response = session.put(api_url, json=post_data)

            # CREATE (if recored doesn't exist, fallback to POST)
            if 'does not exist' in response.text:
                print("CLOUD CREATE:", post_data)
                response = session.post(gs1_products_api_url, json=post_data)
        else:
            # status is "ACTIVE" and new instance: create an item
            print("CLOUD CREATE", post_data)
            response = session.post(gs1_products_api_url, json=post_data)

        response_json = response.json()
        if response_json.get('status') not in (1, 2, 3):
            # reset status if operation is failed,
            # note, we use .update() to avoid this task recursion from .save()
            reset_status = original_instance.gs1_cloud_state if original_instance else 'DRAFT'
            Product.objects.filter(pk=instance.pk).update(
                gs1_cloud_state=reset_status
            )
    elif instance.gs1_cloud_state in ('DRAFT', 'OPTED_OUT'):
        # REMOVE from gs1 cloud
        is_removing_required = (
            original_instance and
            original_instance.pk and
            original_instance.gs1_cloud_state == 'ACTIVE'
        )

        # force override removing if specified
        is_removing_required = is_removing_required or force

        if is_removing_required:
            api_url = f'{gs1_products_api_url}/{instance.gtin}/{instance.target_market.code}'
            print("CLOUD DELETE:", api_url)
            response = session.delete(api_url)

            response_json = response.json()
            if response_json.get('status') != 4:
                # reset status if operation is failed,
                # note, we use .update() to avoid this task recursion from .save()
                reset_status = original_instance.gs1_cloud_state if original_instance else 'ACTIVE'
                Product.objects.filter(pk=instance.pk).update(
                    gs1_cloud_state=reset_status
                )
        else:
            return {
                'info': f'the status {instance.gs1_cloud_state} for {instance} '
                        f'is not intended to update gs1 api cloud'}

    if response_json:
        print(response_json)
        log_gs1_response(user, instance, response_json)

    return {
        'api_response_status': response.status_code if response else None,
        'response_text': response.text if response else None,
    }
