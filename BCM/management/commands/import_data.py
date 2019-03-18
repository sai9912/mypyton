import csv
import json
import zipfile
from collections import namedtuple
from datetime import datetime
from os import makedirs
from os.path import join

import pytz
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation
from prefixes.models import Prefix
from products.models.country_of_origin import CountryOfOrigin
from products.models.dimension_uom import DimensionUOM
from products.models.net_content_uom import NetContentUOM
from products.models.product import Product, Language
from products.models.target_market import TargetMarket
from products.models.weight_uom import WeightUOM
from BCM.helpers.utils import resolve_boolean_value

IMPORT_DEBUG = False

class Command(BaseCommand):
    help = "Command to load data"

    def add_arguments(self, parser):
        parser.add_argument('zip_file_path', nargs='?', default='deployment/deployment-v1-2018-03/sample_data.zip',
                            type=str)

    def handle(self, *args, **options):
        """

        why using get_or_create instead of bulk create?
            if there is one error data then neither of the data get inserted. so we are using get_or_create instead of
            bulk_create
        """

        # currently I have assumed extracted folder, but later can take zip and extract it at particular path
        # I have tried to read csv file directly from zip file but not succeed. will try this also later after
        # completing the main program
        DIR_NAME = '/tmp/deployment/deployment-v1-2018-03/sample_data'

        makedirs(DIR_NAME, exist_ok=True)

        zip_ref = zipfile.ZipFile(options['zip_file_path'], 'r')
        zip_ref.extractall(DIR_NAME)
        zip_ref.close()

        folder_path = DIR_NAME

        CompanyTuple = namedtuple(
            'CompanyTuple',
            ["id", "country", "company", "street1", "street2", "city", "state", "zip",
             "phone",
             "gln", "vat", "credit_points_balance", "prefix_override", "uuid", "active"])

        try:
            member_organization = MemberOrganisation.objects.get(slug='gs1ie')
        except ObjectDoesNotExist:
            print("Unable to find `gs1ie` member organization. so skipping the data load")
            return
        # loading company data
        print("*" * 80) if IMPORT_DEBUG else 0
        try:
            with open(join(folder_path, 'SELECT_t___FROM_public_organisations_t.csv'),
                      newline="\n") as company_csv_file:
                company_csv = csv.reader(company_csv_file, delimiter=',', quotechar='"')
                print('Loading Company Data...', ' Initial Count: ',
                      CompanyOrganisation.objects.count()) if IMPORT_DEBUG else 0
                for row in company_csv:
                    company_data = CompanyTuple(*row)
                    try:
                        company, created = CompanyOrganisation.objects.get_or_create(
                            # why using name? because we might have company_id reference at other tables.
                            # issue: if id vale match with the one at db then it will create serious problem. will fix this later
                            id=company_data.id,
                            uuid=company_data.uuid,
                            member_organisation_id=member_organization.pk,
                            defaults=dict(
                                # why this for name? because we can only have 100 company with no slug and slug is
                                # computed based on name
                                name=company_data.company or company_data.uuid or company_data.id,
                                company=company_data.company,
                                street1=company_data.street1,
                                street2=company_data.street2,
                                city=company_data.city,
                                state=company_data.state,
                                zip=company_data.zip,
                                phone=company_data.phone,
                                gln=company_data.gln,
                                vat=company_data.vat,
                                credit_points_balance=company_data.credit_points_balance,
                                active=resolve_boolean_value(company_data.active),
                                prefix_override=company_data.prefix_override
                            )
                        )
                    except Exception as e:
                        print(e)
                        print("Company Organization: ", row)
                        # print(company.id, company.company, company.slug, company_data.id)
                print('Loading Company Data... Completed', ' Final Count: ',
                      CompanyOrganisation.objects.count()) if IMPORT_DEBUG else 0
        except Exception as e:
            print(str(e))

        ##############################################################################################################
        print("*" * 80) if IMPORT_DEBUG else 0
        UserTuple = namedtuple(
            'UserTuple', ["id", "email", "username", "password", "first_name", "last_name", "active",
                          "confirmed_at", "stripe_id", "customer_role", "last_login", "date_joined",
                          "last_login_at", "current_login_at", "last_login_ip", "current_login_ip",
                          "login_count", "agreed", "agreed_date", "agreed_version", "advanced_tab",
                          "enable_leading", "organisation_id"])

        # loading user data
        try:
            with open(join(folder_path, 'SELECT_t___FROM_public_users_t.csv'), newline="\n") as  user_csv_file:
                user_csv = csv.reader(user_csv_file, delimiter=',', quotechar='"')
                print('Loading user data... ', 'Initial Count: ', User.objects.count()) if IMPORT_DEBUG else 0
                # hash password might not be useful for django as it is depend on hash algorithm and secret
                for number, row in enumerate(user_csv):
                    try:
                        user_data = UserTuple(*row)
                        user_defaults = dict(
                            email=user_data.email,
                            password=user_data.password,
                            first_name=user_data.first_name,
                            last_name=user_data.last_name,
                            is_active=resolve_boolean_value(user_data.active),
                        )
                        if user_data.date_joined:
                            user_defaults['date_joined'] = pytz.utc.localize(
                                datetime.strptime(user_data.date_joined, '%Y-%m-%d %H:%M:%S.%f'))
                        user, created = User.objects.get_or_create(
                            username=user_data.username,
                            id=user_data.id,
                            defaults=user_defaults
                            # remaining fields
                            # confirmed_at, stripe_id, "current_login_at", "last_login_ip", "current_login_ip",
                            #  "enable_leading", "organisation_id"

                        )
                        profile = user.profile
                        profile.active = resolve_boolean_value(user_data.active)
                        profile.customer_role = user_data.customer_role
                        profile.agreed = resolve_boolean_value(user_data.agreed)

                        if user_data.agreed_date:
                            profile.agreed_date = pytz.utc.localize(
                                datetime.strptime(user_data.agreed_date, '%Y-%m-%d %H:%M:%S.%f'))

                        profile.agreed_version = user_data.agreed_version

                        if user_data.login_count:
                            profile.login_count = user_data.login_count
                        profile.advanced_tab = resolve_boolean_value(user_data.advanced_tab)
                        profile.save()
                    except Exception as e:
                        print(e)
                        print("User Data: ", row)
                        # print('row number:', number, " user id: ", user.id, user.email)
                print('Loading user data... Completed. ', 'Final Count: ', User.objects.count()) if IMPORT_DEBUG else 0
        except Exception as e:
            print(str(e))

        #############################################################################################################
        print("*" * 80) if IMPORT_DEBUG else 0
        PrefixTuple = namedtuple(
            'PrefixTuple',
            ["id", "prefix", "is_active", "created", "updated", "starting_from", "organisation_id",
             "is_suspended", "is_special", "description", "starting_from_gln"])
        # loading prefix data
        try:
            with open(join(folder_path, 'SELECT_t___FROM_public_prefixes_t.csv'), newline="\n") as  prefix_csv_file:
                prefix_csv = csv.reader(prefix_csv_file, delimiter=',', quotechar='"')
                print('Loading prefix data... ', 'Initial Count: ', Prefix.objects.count()) if IMPORT_DEBUG else 0
                for number, row in enumerate(prefix_csv):
                    try:
                        prefix_data = PrefixTuple(*row)

                        prefix_defaults = dict(
                            is_active=resolve_boolean_value(prefix_data.is_active),
                            is_suspended=resolve_boolean_value(prefix_data.is_suspended),
                            is_special=prefix_data.is_special,
                            description=prefix_data.description
                        )
                        if prefix_data.created:
                            prefix_defaults['created'] = pytz.utc.localize(
                                datetime.strptime(prefix_data.created, '%Y-%m-%d %H:%M:%S.%f'))
                        if prefix_data.updated:
                            prefix_defaults['updated'] = pytz.utc.localize(
                                datetime.strptime(prefix_data.updated, '%Y-%m-%d %H:%M:%S.%f'))
                        if prefix_data.starting_from:
                            prefix_defaults['starting_from'] = prefix_data.starting_from
                        if prefix_data.starting_from_gln:
                            prefix_defaults['starting_from_gln'] = prefix_data.starting_from_gln

                        Prefix.objects.get_or_create(
                            id=prefix_data.id,
                            prefix=prefix_data.prefix,
                            member_organisation_id=member_organization.pk,
                            company_organisation_id=prefix_data.organisation_id,
                            defaults=prefix_defaults,
                        )
                    except Exception as e:
                        print(e)
                        print("Prefix Data: ", row)
                print('Loading prefix data... Completed. ', 'Final Count: ',
                      Prefix.objects.count()) if IMPORT_DEBUG else 0
        except Exception as e:
            print(str(e))

        ##############################################################################################################
        print("*" * 80) if IMPORT_DEBUG else 0
        CountryOfOriginTuple = namedtuple('CountryOfOrigin', ['id', 'code', 'name'])
        try:
            with open(join(folder_path, 'SELECT_t___FROM_public_country_of_origin.csv'),
                      newline="\n") as country_of_origin_file:
                country_of_origin_csv = csv.reader(country_of_origin_file, delimiter=',', quotechar='"')
                print('Loading Country data... ', 'Initial Count: ',
                      CountryOfOrigin.objects.count()) if IMPORT_DEBUG else 0
                for row_number, row in enumerate(country_of_origin_csv):
                    country_of_origin_data = CountryOfOriginTuple(*row)
                    try:
                        CountryOfOrigin.objects.get_or_create(
                            id=country_of_origin_data.id,
                            code=country_of_origin_data.code,
                            name=country_of_origin_data.name)
                    except Exception as e:
                        print(e)
                        print("Country Data: ", row)
                print('Loading Country data... Completed', 'Final Count: ',
                      CountryOfOrigin.objects.count()) if IMPORT_DEBUG else 0
        except Exception as e:
            print(e)

        print("*" * 80) if IMPORT_DEBUG else 0
        DimensionUOMTuple = namedtuple('DimensionUOM', ['id', 'uom', 'abbr', 'code'])
        try:
            with open(join(folder_path, 'SELECT_t___FROM_public_dimension_uom_t.csv'),
                      newline="\n") as dimension_uom_csv_file:
                dimension_uom_csv = csv.reader(dimension_uom_csv_file, delimiter=',', quotechar='"')
                print('Loading dimension uom data... ', 'Initial Count: ',
                      DimensionUOM.objects.count()) if IMPORT_DEBUG else 0
                for row_number, row in enumerate(dimension_uom_csv):
                    dimension_uom_data = DimensionUOMTuple(*row)
                    try:
                        duom, created = DimensionUOM.objects.get_or_create(
                            id=dimension_uom_data.id,
                            uom=dimension_uom_data.uom,
                            abbr=dimension_uom_data.abbr,
                            code=dimension_uom_data.code
                        )
                    except Exception as e:
                        print(e)
                        print("Dimension UOM Data: ", row)
                print('Loading dimension uom data... Completed. ', 'Final Count: ',
                      DimensionUOM.objects.count()) if IMPORT_DEBUG else 0

        except Exception as e:
            print(e)

        print("*" * 80) if IMPORT_DEBUG else 0
        LanguageTuple = namedtuple('LanguageTuple', ['id', 'name', 'slug'])
        try:
            with open(join(folder_path, 'SELECT_t___FROM_public_language_t.csv'), newline="\n") as language_csv_file:
                language_csv = csv.reader(language_csv_file, delimiter=',', quotechar='"')
                print('Loading language data... ', 'Initial Count: ', Language.objects.count()) if IMPORT_DEBUG else 0
                for row_number, row in enumerate(language_csv):
                    language_data = LanguageTuple(*row)
                    try:
                        Language.objects.get_or_create(
                            id=language_data.id,
                            name=language_data.name,
                            slug=language_data.slug)
                    except Exception as e:
                        print(e)
                        print("Language Data: ", row)
                print('Loading language data... Completed. ', 'Final Count: ',
                      Language.objects.count()) if IMPORT_DEBUG else 0
        except Exception as e:
            print(e)

        print("*" * 80) if IMPORT_DEBUG else 0
        NetContentUOMTuple = namedtuple('NetContentUOMTuple', ['id', 'uom', 'abbr', 'code'])
        try:
            with open(join(folder_path, 'SELECT_t___FROM_public_net_content_uom_t.csv'),
                      newline="\n") as net_content_uom_csv_file:
                net_content_uom_csv = csv.reader(net_content_uom_csv_file, delimiter=',', quotechar='"')
                print('Loading Net Content UOM data... ', 'Initial Count: ',
                      NetContentUOM.objects.count()) if IMPORT_DEBUG else 0
                for row_number, row in enumerate(net_content_uom_csv):
                    net_content_uom_data = NetContentUOMTuple(*row)
                    try:
                        NetContentUOM.objects.get_or_create(
                            id=net_content_uom_data.id,
                            uom=net_content_uom_data.uom,
                            abbr=net_content_uom_data.abbr,
                            # code=net_content_uom_data.code
                        )
                    except Exception as e:
                        print(e)
                        print("Net Content UOM Data: ", row)
                print('Loading Net Content UOM data... Completed.', 'Final Count: ',
                      NetContentUOM.objects.count()) if IMPORT_DEBUG else 0
        except Exception as e:
            print(e)

        print("*" * 80) if IMPORT_DEBUG else 0
        TargetMarketTuple = namedtuple('TargetMarket', ['id', 'code', 'market'])
        try:
            with open(join(folder_path, 'SELECT_t___FROM_public_target_market_t.csv'),
                      newline="\n") as target_market_csv_file:
                target_market_csv = csv.reader(target_market_csv_file, delimiter=',', quotechar='"')
                print('Loading target market data... ', 'Initial Count: ',
                      TargetMarket.objects.count()) if IMPORT_DEBUG else 0
                for row_number, row in enumerate(target_market_csv):
                    target_market_data = TargetMarketTuple(*row)
                    try:
                        TargetMarket.objects.get_or_create(
                            id=target_market_data.id,
                            code=target_market_data.code,
                            market=target_market_data.market
                        )
                    except Exception as e:
                        print(e)
                        print("Target Market: ", row)
                print('Loading target market data... Completed. ', 'Final Count: ',
                      TargetMarket.objects.count()) if IMPORT_DEBUG else 0
        except Exception as e:
            print(e)

        print("*" * 80) if IMPORT_DEBUG else 0
        WeightUOMTuple = namedtuple('WeightUOMTuple', ['id', 'uom', 'abbr', 'code'])
        try:
            with open(join(folder_path, 'SELECT_t___FROM_public_weight_uom_t.csv'), newline="\n") as product_csv_file:
                product_csv = csv.reader(product_csv_file, delimiter=',', quotechar='"')
                print('Loading weight uom data... ', 'Initial Count: ', WeightUOM.objects.count()) if IMPORT_DEBUG else 0
                for row_number, row in enumerate(product_csv):
                    weight_uom_data = WeightUOMTuple(*row)
                    try:
                        WeightUOM.objects.get_or_create(
                            id=weight_uom_data.id,
                            uom=weight_uom_data.uom,
                            abbr=weight_uom_data.abbr,
                            code=weight_uom_data.code
                        )
                    except Exception as e:
                        print(e)
                        print("Target Market: ", row)
                print('Loading weight uom data... Completed. ', 'Final Count: ', WeightUOM.objects.count()) if IMPORT_DEBUG else 0

        except Exception as e:
            print(e)

        print("*" * 80) if IMPORT_DEBUG else 0
        # loading product data
        ProductTuple = namedtuple(
            'ProductTuple',
            ["id", "owner_id", "gtin", "gs1_company_prefix", "gln_of_information_provider",
             "category", "attributes", "package_level_id", "package_type_id", "description",
             "sku", "brand", "sub_brand", "functional_name", "variant",
             "net_content_uom_id", "net_content", "image", "depth", "width", "height",
             "gross_weight", "net_weight", "point_of_sale", "company", "contact", "address",
             "company_phone", "company_email", "bar_type", "bar_placement", "avail_barcode_height",
             "avail_barcode_width", "country_of_origin_id", "website_url", "enquiries", "is_cunit",
             "is_dunit", "is_vunit", "is_iunit", "is_ounit", "is_temp", "is_active", "is_public",
             "pub_date", "created", "updated", "additional_classification_code",
             "additional_identification_of_ip", "brand_owner_gln", "brand_owner_name",
             "category_definition", "category_name", "depth_uom_id", "descriptive_size",
             "discontinued_date", "eff_date", "end_availability", "gross_weight_uom_id",
             "height_uom_id", "is_bunit", "is_price_on_pack", "language_id", "last_change",
             "manufacturer_additional_identification", "manufacturer_gln", "manufacturer_name",
             "manufacturer_role_id", "mark", "name_of_information_provider", "net_weight_uom_id",
             "returnable", "role_of_information_provider_id", "size_code", "start_availability",
             "target_market_id", "width_uom_id", "labelDescription", "gs1_cloud_last_rc",
             "gs1_cloud_last_update", "gs1_cloud_last_update_ref", "gs1_cloud_state",
             "organisation_id"])

        with open(join(folder_path, 'SELECT_t___FROM_public_products_t.csv'), newline="\n") as product_csv_file:
            product_csv = csv.reader(product_csv_file, delimiter=',', quotechar='"')
            print('Loading product data... ', 'Initial Count: ', Product.objects.count()) if IMPORT_DEBUG else 0
            for row_number, row in enumerate(product_csv):
                if len(row) == 83:

                    product_data = ProductTuple(*row)
                    product_default = dict(
                        gtin=product_data.gtin,
                        gs1_company_prefix=product_data.gs1_company_prefix,
                        gln_of_information_provider=product_data.gln_of_information_provider,
                        category=product_data.category,
                        label_description_i18n=json.dumps({'en': product_data.labelDescription}),
                        gs1_cloud_state=product_data.gs1_cloud_state,
                        description_i18n=json.dumps({'en': product_data.description}),
                        sku=product_data.sku,
                        brand_i18n=json.dumps({'en': product_data.brand}),
                        sub_brand=product_data.sub_brand,
                        functional_name_i18n=json.dumps({'en': product_data.functional_name}),
                        variant=product_data.variant,
                        net_content=product_data.net_content,
                        net_content_uom_id=product_data.net_content_uom_id,
                        company=product_data.company,
                        bar_placement=product_data.bar_placement,
                        country_of_origin_id=product_data.country_of_origin_id,
                        point_of_sale=product_data.point_of_sale,
                        website_url=product_data.website_url,
                        is_bunit=resolve_boolean_value(product_data.is_bunit),
                        is_cunit=resolve_boolean_value(product_data.is_cunit),
                        is_dunit=resolve_boolean_value(product_data.is_dunit),
                        is_vunit=resolve_boolean_value(product_data.is_vunit),
                        is_iunit=resolve_boolean_value(product_data.is_iunit),
                        is_ounit=resolve_boolean_value(product_data.is_ounit),
                        name_of_information_provider=product_data.name_of_information_provider,
                        target_market_id=product_data.target_market_id or None,
                        language_id=product_data.language_id or None,
                    )

                    if product_data.created:
                        product_default['created'] = pytz.utc.localize(
                            datetime.strptime(product_data.created, '%Y-%m-%d %H:%M:%S.%f'))

                    if product_data.updated:
                        product_default['updated'] = pytz.utc.localize(
                            datetime.strptime(product_data.updated, '%Y-%m-%d %H:%M:%S.%f'))

                    if product_data.net_weight:
                        product_default['net_weight'] = product_data.net_weight

                    if product_data.net_weight_uom_id:
                        product_default['net_weight_uom_id'] = product_data.net_weight_uom_id,

                    if product_data.gross_weight:
                        product_default['gross_weight'] = product_data.gross_weight

                    if product_data.gross_weight_uom_id:
                        product_default['gross_weight_uom_id'] = product_data.gross_weight_uom_id,

                    if product_data.depth:
                        product_default['depth'] = product_data.depth

                    if product_data.depth_uom_id:
                        product_default['depth_uom_id'] = product_data.depth_uom_id

                    if product_data.width:
                        product_default['width'] = product_data.width

                    if product_data.width_uom_id:
                        product_default['width_uom_id'] = product_data.width_uom_id

                    if product_data.height:
                        product_default['height'] = product_data.height

                    if product_data.height_uom_id:
                        product_default['height_uom_id'] = product_data.height_uom_id

                    # package_level, package_type
                    if product_data.mark:
                        product_default['mark'] = product_data.mark

                    Product.objects.get_or_create(
                        id=product_data.id,
                        owner_id=product_data.owner_id,
                        company_organisation_id=product_data.organisation_id,
                        member_organisation_id=member_organization.pk,
                        defaults=product_default
                    )

                else:
                    print(
                        ">>> Have not added this record as field value missmatched. required: 83. but have: {0}".format(
                            len(row))) if IMPORT_DEBUG else 0
                    print(row) if IMPORT_DEBUG else 0
            print('Loading product data... completed. ', 'Final Count: ',
                  Product.objects.count()) if IMPORT_DEBUG else 0


        ##############################################################################################################
        # SubProductTuple = namedtuple(
        #         'SubProductTuple',
        #         ["id", "product_id", "sub_product_id", "quantity", "constraint"])
        # loading sub product data
        # try:
        #     with open(join(folder_path, 'SELECT_t___FROM_public_sub_products_t.csv'),
        #               newline="\n") as sub_product_csv_file:
        #         sub_product_csv = csv.reader(sub_product_csv_file, delimiter=',', quotechar='"')
        #         for row in sub_product_csv:
        #             pass
        #             sub_product_data = SubProductTuple(*row)
        # except Exception as e:
        #     print(str(e))
