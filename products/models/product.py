import datetime
import json
import operator

import django_filters
from crequest.middleware import CrequestMiddleware
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import gettext as _

from audit.models import cloud_log_service
from BCM.helpers import test_helpers
from BCM.helpers.translation_helpers import TranslatedFieldsMixin
from cloud.utils import cloud_add, cloud_delete
from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation
from products.helpers import product_helper
from products.tasks import update_gs1_cloud_product
from .country_of_origin import CountryOfOrigin
from .dimension_uom import DimensionUOM
from .language import Language
from .net_content_uom import NetContentUOM
from .package_level import PackageLevel
from .package_type import PackageType
from .target_market import TargetMarket
from .weight_uom import WeightUOM
from django.shortcuts import get_object_or_404


class ServiceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def create_prod(self, **kwargs):
        pass

    def check_instance(self, instance):
        result = isinstance(instance, Product)
        if not result:
            raise ValueError('%s is not of type %s' % (instance, Product))
        return True

    def save(self, product):
        self.check_instance(product)
        product.save()

    def get_or_create(self, **kwargs):
        return super().get_or_create(**kwargs)

    def create(self, **kwargs):
        fields_data = {}

        for field in Product._meta.get_fields():
            if field.name in kwargs.keys():
                if field.name in ['depth_uom', 'width_uom', 'height_uom']:
                    if type(kwargs[field.name]) is str:
                        row = DimensionUOM.objects.get(code=kwargs[field.name])
                        if row:
                            fields_data[field.name] = row
                    else:
                        fields_data[field.name] = kwargs[field.name]
                elif field.name in ['gross_weight_uom', 'net_weight_uom']:
                    if type(kwargs[field.name]) is str:
                        row = WeightUOM.objects.get(code=kwargs[field.name])
                        if row:
                            fields_data[field.name] = row
                    else:
                        fields_data[field.name] = kwargs[field.name]
                elif field.name == 'country_of_origin':
                    if type(kwargs[field.name]) is str:
                        row = CountryOfOrigin.objects.get(
                            code=kwargs[field.name])
                        if row:
                            fields_data[field.name] = row
                    else:
                        fields_data[field.name] = kwargs[field.name]
                elif field.name == 'target_market':
                    if type(kwargs[field.name]) is str:
                        row = TargetMarket.objects.get(code=kwargs[field.name])
                        if row:
                            fields_data[field.name] = row
                    else:
                        fields_data[field.name] = kwargs[field.name]
                elif field.name == 'language':
                    if type(kwargs[field.name]) is str:
                        row = Language.objects.get(slug=kwargs[field.name])
                        if row:
                            fields_data[field.name] = row
                    else:
                        fields_data[field.name] = kwargs[field.name]
                elif field.name == 'package_level':
                    if type(kwargs[field.name]) is str:
                        row = PackageLevel.objects.get(id=kwargs[field.name])
                        if row:
                            fields_data[field.name] = row
                    else:
                        fields_data[field.name] = kwargs[field.name]
                elif field.name == 'package_type':
                    if type(kwargs[field.name]) is str:
                        row = PackageType.objects.get(id=kwargs[field.name])
                        if row:
                            fields_data[field.name] = row
                    else:
                        fields_data[field.name] = kwargs[field.name]
                elif field.name == "owner":
                    if type(kwargs[field.name]) is str:
                        row = User.objects.get(id=kwargs[field.name])
                        if row:
                            fields_data[field.name] = row
                    else:
                        fields_data[field.name] = kwargs[field.name]

                elif field.name in ['is_bunit', 'is_cunit', 'is_dunit', 'is_vunit', 'is_iunit', 'is_ounit']:
                    if type(kwargs[field.name]) is str:
                        if kwargs[field.name] == 'on':
                            fields_data[field.name] = True
                        else:
                            fields_data[field.name] = False
                    else:
                        fields_data[field.name] = kwargs[field.name]
                elif field.name.endswith('_i18n'):
                    # localized fields
                    value = kwargs[field.name]
                    if isinstance(value, str):
                        fields_data[field.name] = kwargs[field.name]
                    elif isinstance(value, dict):
                        fields_data[field.name] = json.dumps(kwargs[field.name])
                else:
                    fields_data[field.name] = kwargs[field.name]

        if kwargs.get('prefix'):
            prefix = kwargs['prefix']
            fields_data['gs1_company_prefix'] = prefix.prefix
            fields_data['company_organisation_id'] = prefix.company_organisation.id
            fields_data['member_organisation_id'] = prefix.member_organisation.pk

        product = Product(**fields_data)
        product.save()

        from .gtin_target_market import gtin_target_market_service
        gtin_target_market_service.create(product, fields_data['target_market'])

        return product

    def get_my_product(self, owner, product_id):
        """
        validates product ownership given PK
        :param owner: owner of the product
        :param product_id: pk
        :return: product instance
        """

        return get_object_or_404(
            Product,
            id=product_id,
            company_organisation=owner.profile.company_organisation
        )

    def get_by_gtin(self, owner, gtin):
        """
        validates product ownership given PK
        :param owner: owner of the product
        :param gtin: GTIN
        :return: product instance
        """

        return get_object_or_404(
            Product,
            gtin=gtin,
            company_organisation=owner.profile.company_organisation
        )

    def get_available_subproducts(self, owner, package_level):
        """return products which can be choisen as subproducts"""
        owner_id = getattr(owner, 'id', False)
        if not owner_id:
            # if owner is not provided return no objects
            return self.model.objects.none()

        products = self.model.objects.filter(owner_id=owner_id)

        package_level_id = getattr(package_level, 'id', False)

        if not package_level_id:
            # if package_level id is not provided return no objects
            return products.none()

        if package_level_id == PackageLevel.BASE:
            # base can not have children
            return products.none()

        if package_level_id == PackageLevel.PACK:
            # Pack can include Pack or Base (__gte)
            return products.filter(package_level_id__gte=package_level_id)

        if package_level_id == PackageLevel.CASE:
            # Case can include Case, Pack or Base
            return products.filter(package_level_id__gte=package_level_id)

        if package_level_id == PackageLevel.PALLET:
            # PALLET can not be included in another PALLET
            return products.exclude(package_level_id=package_level_id)

        # if other packege level provided return no objects
        return products.none()

    def check_subproducts(self, sub_product_gtins, package_level, owner):
        """Check products whick user wants to include in product as subproducts"""

        sub_product_gtins = set(sub_product_gtins)

        sub_products = Product.objects.filter(
            gtin__in=sub_product_gtins,
            owner=owner
        )
        if len(sub_products) != len(sub_product_gtins):
            return {
                'is_valid': False,
                'error': 'You can include only your products'
            }

        if package_level.id == PackageLevel.BASE and len(sub_products):
            return {
                'is_valid': False,
                'error': 'Base can not include sub products'
            }

        return {'is_valid': True}

    def _get_fields_data(self, **kwargs):
        fields_data = {}
        for field in Product._meta.get_fields():
            try:
                if field.name in kwargs.keys():
                    if field.name in ['depth_uom', 'width_uom', 'height_uom']:
                        if type(kwargs[field.name]) is str:
                            if kwargs.get("use_ids"):
                                row = DimensionUOM.objects.get(
                                    id=kwargs[field.name])
                            else:
                                row = DimensionUOM.objects.get(
                                    code=kwargs[field.name])
                            if row:
                                fields_data[field.name] = row
                        else:
                            fields_data[field.name] = kwargs[field.name]
                    elif field.name in ['gross_weight_uom', 'net_weight_uom']:
                        if type(kwargs[field.name]) is str:
                            if kwargs.get("use_ids"):
                                row = WeightUOM.objects.get(
                                    id=kwargs[field.name])
                            else:
                                row = WeightUOM.objects.get(
                                    code=kwargs[field.name])
                            if row:
                                fields_data[field.name] = row
                        else:
                            fields_data[field.name] = kwargs[field.name]
                    elif field.name in ['net_content_uom']:
                        if type(kwargs[field.name]) is str:
                            if kwargs.get("use_ids"):
                                row = NetContentUOM.objects.get(
                                    id=kwargs[field.name])
                            else:
                                row = NetContentUOM.objects.get(
                                    code=kwargs[field.name])
                            if row:
                                fields_data[field.name] = row
                        else:
                            fields_data[field.name] = kwargs[field.name]

                    elif field.name == 'country_of_origin':
                        if type(kwargs[field.name]) is str:
                            if kwargs.get("use_ids"):
                                row = CountryOfOrigin.objects.get(
                                    id=kwargs[field.name])
                            else:
                                row = CountryOfOrigin.objects.get(
                                    code=kwargs[field.name])
                            if row:
                                fields_data[field.name] = row
                        else:
                            fields_data[field.name] = kwargs[field.name]
                    elif field.name == 'target_market':
                        if type(kwargs[field.name]) is str:
                            if kwargs.get("use_ids"):
                                row = TargetMarket.objects.get(
                                    id=kwargs[field.name])
                            else:
                                row = TargetMarket.objects.get(
                                    code=kwargs[field.name])
                            if row:
                                fields_data[field.name] = row
                        else:
                            fields_data[field.name] = kwargs[field.name]
                    elif field.name == 'language':
                        if type(kwargs[field.name]) is str:
                            if kwargs.get("use_ids"):
                                row = Language.objects.get(id=kwargs[field.name])
                            else:
                                row = Language.objects.get(slug=kwargs[field.name])
                            if row:
                                fields_data[field.name] = row
                        else:
                            fields_data[field.name] = kwargs[field.name]
                    elif field.name == 'package_level':
                        if type(kwargs[field.name]) is str:
                            row = PackageLevel.objects.get(
                                id=kwargs[field.name])
                            if row:
                                fields_data[field.name] = row
                        else:
                            fields_data[field.name] = kwargs[field.name]
                    elif field.name == 'package_type':
                        if type(kwargs[field.name]) is str and kwargs[field.name]:
                            row = PackageType.objects.get(
                                    id=kwargs[field.name])
                            if row:
                                fields_data[field.name] = row
                        else:
                            fields_data[field.name] = kwargs[field.name]
                    elif field.name in ['is_bunit', 'is_cunit', 'is_dunit', 'is_vunit', 'is_iunit', 'is_ounit']:
                        if type(kwargs[field.name]) is str:
                            if kwargs[field.name] == 'on':
                                fields_data[field.name] = True
                            else:
                                fields_data[field.name] = False
                        else:
                            fields_data[field.name] = kwargs[field.name]
                    else:
                        fields_data[field.name] = kwargs[field.name]
            except Exception as err:
                print(field.name, err)
                pass

        if kwargs.get('prefix'):
            fields_data['gs1_company_prefix'] = kwargs['prefix'].prefix

        return fields_data

    def _rc_to_val(self, rc):
        product_record_created = 1
        product_record_modified = 2
        product_record_refreshed = 3
        product_record_deleted = 4
        operation_failed = 5
        not_authorized_to_perform_this_operation = 6
        key_is_valid = 7
        key_is_not_valid = 8

        gs1_cloud_rc_enum = {
            product_record_created: 'PRODUCT_RECORD_CREATED',
            product_record_modified: 'PRODUCT_RECORD_MODIFIED',
            product_record_refreshed: 'PRODUCT_RECORD_REFRESHED',
            product_record_deleted: 'PRODUCT_RECORD_DELETED',
            operation_failed: 'OPERATION_FAILED',
            not_authorized_to_perform_this_operation: 'NOT_AUTHORIZED_TO_PERFORM_THIS_OPERATION',
            key_is_valid: 'KEY_IS_VALID',
            key_is_not_valid: 'KEY_IS_NOT_VALID'
        }

        val = gs1_cloud_rc_enum.get(rc, 'NOT_IMPLEMENTED')
        return val

    def update(self, product, **kwargs):
        fields_data = self._get_fields_data(**kwargs)
        user = kwargs['owner']
        update_cloud_fl = (fields_data['gs1_cloud_state'] != product.gs1_cloud_state)

        for field in fields_data:
            setattr(product, field, fields_data[field])
        product.save()

        if update_cloud_fl:
            if product.gs1_cloud_state == 'ACTIVE':
                res = cloud_add(user, product)
            else:
                res = cloud_delete(user, product)

            cloud_log_service.log(user=user,
                                  key=res.get('gtin'),
                                  gs1_cloud_last_rc=self._rc_to_val(res.get('status', 0)),
                                  msg=res.get('message'),
                                  ref=res.get('ref'))

        return product


class Product(models.Model, TranslatedFieldsMixin):
    # product owner info
    owner = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE)

    # company organisation
    company_organisation = models.ForeignKey(
        CompanyOrganisation, null=True, on_delete=models.PROTECT)

    # member organisation
    member_organisation = models.ForeignKey(
        MemberOrganisation, null=True, on_delete=models.PROTECT)

    # GDD: GlobalTradeItemNumber
    gtin = models.CharField(max_length=14, default='',
                            blank=True, db_index=True, unique=True)
    # GCP
    gs1_company_prefix = models.CharField(
        max_length=75, default='', blank=True, db_index=True)

    # GDD: InformationProvider
    gln_of_information_provider = models.CharField(max_length=75, null=True)

    # GDD: ClassificationCategoryCode
    category = models.CharField(max_length=75, null=True)

    # GDD: LabelDescription
    label_description_i18n = models.TextField(default='{}', null=True)

    # GDD: TradeItemUnitDescriptor
    package_level = models.ForeignKey(
        PackageLevel, null=True, blank=True, on_delete=models.CASCADE
    )

    # GDD: PackagingType
    package_type = models.ForeignKey(
        PackageType, null=True, blank=True, on_delete=models.CASCADE
    )

    # GDD: TradeItemDescription
    description_i18n = models.TextField(default='{}', null=True)

    # GDD: AdditionalTradeItemIdentificationValue
    sku = models.CharField(max_length=75, null=True)

    # GDD: AdditionalTradeItemIdentificationType
    additional_trade_item_id_type = models.CharField(max_length=75, null=True, default='SUPPLIER_ASSIGNED')

    # GDD: Type Of Information
    type_of_information = models.CharField(max_length=75, null=True, default='PRODUCT_IMAGE')

    # GDD: BrandName
    brand_i18n = models.TextField(default='{}', null=True)

    # GDD: SubBrand
    sub_brand = models.CharField(max_length=75, null=True)

    # GDD: FunctionalName
    functional_name_i18n = models.TextField(default='{}', null=True)

    # GDD: VariantText
    variant = models.CharField(max_length=75, null=True)

    # not in gdd
    # use product.add_image(request.files['img']) method to save image
    image_i18n = models.TextField(default='{}', null=True)

    # -- Dimensions --

    # GDD: Depth
    depth = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    # GDD: Depth UOM
    depth_uom = models.ForeignKey(
        DimensionUOM, null=True, on_delete=models.CASCADE, related_name='products_depth_uom'
    )

    # GDD: Width
    width = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    # GDD: Width UOM
    width_uom = models.ForeignKey(
        DimensionUOM, null=True, on_delete=models.CASCADE, related_name='products_width_uom'
    )

    # GDD: Height
    height = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    # GDD: Height UOM
    height_uom = models.ForeignKey(
        DimensionUOM, null=True, on_delete=models.CASCADE, related_name='products_height_uom'
    )

    # -- Qualified  values --

    # GDD: NetContent
    net_content = models.CharField(max_length=10, null=True)

    # GDD: NetContent UOM
    net_content_uom = models.ForeignKey(
        NetContentUOM, null=True, on_delete=models.CASCADE, related_name='products_netcontent_uom'
    )

    # GDD: GrossWeight
    gross_weight = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    # GDD: GrossWeight UOM
    gross_weight_uom = models.ForeignKey(
        WeightUOM, null=True, on_delete=models.CASCADE, related_name='products_grossweight_uom'
    )

    # GDD: NetWeight
    net_weight = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    # GDD: NetWeight UOM
    net_weight_uom = models.ForeignKey(
        WeightUOM, null=True, on_delete=models.CASCADE, related_name='products_netweight_uom'
    )

    # GDD: CompanyName
    company = models.CharField(max_length=100, null=True)

    # GDD: BarCodeType
    # db.Enum('NULL', 'UPCA', 'EAN13', 'RSS14', 'ISBN13', 'ITF14')
    bar_type = models.CharField(max_length=10, default='EAN13')

    # GDD: ???
    bar_placement = models.CharField(max_length=50, null=True)

    # GDD: TradeItemCountryOfOrigin
    country_of_origin = models.ForeignKey(CountryOfOrigin, null=True, on_delete=models.CASCADE)

    # GDD: ???
    point_of_sale = models.CharField(max_length=75, null=True)

    # GDD: Uniform Resource Identifier
    website_url = models.CharField(max_length=256, null=True)

    # -- Booleans --

    # GDD: IsTradeItemABaseUnit
    is_bunit = models.BooleanField(default=False)

    # GDD: IsTradeItemAConsumerUnit
    is_cunit = models.BooleanField(default=False)

    # GDD: IsTradeItemAVariableUnit
    is_vunit = models.BooleanField(default=False)

    # GDD: IsTradeItemAnOrderableUnit
    is_ounit = models.BooleanField(default=False)

    # GDD: IsTradeItemADespatchUnit
    is_dunit = models.BooleanField(default=False)

    # GDD: IsTradeItemAnInvoiceUnit
    is_iunit = models.BooleanField(default=False)

    # -- Dates --

    # GDD: PublicationDate
    pub_date = models.DateTimeField(null=True)  # AQ

    # GDD: EffectiveDate
    eff_date = models.DateTimeField(null=True)  # AR

    # nogdd -- internal
    created = models.DateTimeField(null=True, auto_now_add=True)

    # nogdd -- internal
    updated = models.DateTimeField(null=True, auto_now=True)

    # GDD: StartAvailabilityDateTime
    start_availability = models.DateTimeField(null=True, auto_now=True)

    # GDD: EndAvailabilityDateTime
    end_availability = models.DateTimeField(null=True, auto_now=True)

    # GDD: DiscontinueDateTime
    discontinued_date = models.DateTimeField(null=True)

    # GDD: LastChangeDateTime
    last_change = models.DateTimeField(null=True, auto_now=True)

    #  -- GDSN additions --

    # GDD: NameOfInformationProvider
    name_of_information_provider = models.CharField(max_length=200, null=True)

    # GDD: TargetMarketCountryCodes
    target_market = models.ForeignKey(TargetMarket, null=True, on_delete=models.CASCADE)

    # GDD: Is packaging marked returnable
    returnable = models.BooleanField(default=False)

    # GDD: Is price on Pack
    is_price_on_pack = models.BooleanField(default=False)

    # ???
    brand_owner_gln = models.CharField(max_length=13, null=True)

    # ???
    brand_owner_name = models.CharField(max_length=13, null=True)

    # -- GEPIR additions --

    # GDD: Language Code
    language = models.ForeignKey(Language, null=True, on_delete=models.CASCADE)

    # GDD: NameOfManufacturer (GLN)
    manufacturer_gln = models.CharField(max_length=13, null=True)

    # GDD: NameOfManufacturer
    manufacturer_name = models.CharField(max_length=200, null=True)

    # GDD: CommunicationChannelCode
    communication_channel_code = models.CharField(max_length=13, null=True)

    # GDD: CommunicationValue
    communication_value = models.CharField(max_length=13, null=True)

    # GDD: descriptiveSize
    descriptive_size = models.CharField(max_length=75, null=True)

    # GDD: colourCode
    size_code = models.CharField(max_length=25, null=True)

    #  -- Cloud additions --

    # GDD: GS1 Cloud Status
    gs1_cloud_state = models.CharField(max_length=75, default='INACTIVE')

    # gs1_cloud_state = db.Column(
    #    db.Enum(*GS1_CLOUD_STATES_ENUM.keys(), name='gs1_cloud_state'), default='INACTIVE', nullable=False)
    # gs1_cloud_last_rc = db.Column(db.Enum(*GS1_CLOUD_RC_ENUM.keys(), name='gs1_cloud_rc_enum'), nullable=True)
    # gs1_cloud_last_update = db.Column(db.DateTime())
    # gs1_cloud_last_update_ref = db.Column(db.String(20), nullable=True, index=True)

    # PLACEHOLDER FOR UI ( to be able to favorite an item )
    mark = models.IntegerField(default=0)

    objects = models.Manager()
    service = ServiceManager()

    # Fields not converted yet
    # barcodes = models.ForeignKey('Barcode')

    @property
    def completeness(self):
        comp_fields = [
            'category',
            'description',
            'sku',
            'brand',
            'sub_brand',
            'functional_name',
            'variant',

            'image',
            'depth',
            'height',
            'width',
            'gross_weight',

            'country_of_origin_id',
            'website_url',
        ]

        if self.package_level and self.package_level.id == settings.BASE_PACKAGE_LEVEL:
            comp_fields.extend(['net_weight', 'net_content'])

        cnt_available = 0
        cnt_present = 0

        for comp_field in comp_fields:
            # if self.__getattribute__(comp_field):
            if getattr(self, comp_field):
                cnt_present += 1
            cnt_available += 1

        unit_field_found = False
        cnt_available += 1
        for comp_field in 'is_cunit', 'is_dunit', 'is_vunit', 'is_iunit', 'is_ounit':
            if not unit_field_found:
                # if self.__getattribute__(comp_field):
                if getattr(self, comp_field):
                    unit_field_found = True
        if unit_field_found:
            cnt_present += 1
        return float(cnt_present) / float(cnt_available) * 100

    def get(self, name, default=None):
        try:
            # value = self.__getattribute__(name)
            value = getattr(self, name)
        except:
            value = default
        return value

    # TODO -- begin
    organisation = None
    brand_owner_gln = 'Brand_Owner_GLN'
    brand_owner_name = 'Brand_Owner_Name'
    gtin_of_next_lower_item = 'GTIN_Of_Next_Lower_Item'
    total_quantity_of_next = 'Amount_Of_Next_Lower_Level_Items'
    quantity_of_children = 'Quantity_Of_Children'

    def get_leading(self):
        return '11111111'

    # TODO -- end

    def get_company_organisation(self):
        return self.company_organisation

    def get_member_organisation(self):
        return self.member_organisation

    def to_gdsn(self):
        def internal_bar_type_to_repr(bar_type):
            # for key, value in BARCODE_TYPES.items():
            #    if value == bar_type:
            #        return key
            # logging.error('could not map barcode_type for %s' % self.gtin)
            return 'EAN_13'

        data = {
            'Label_Description': self.label_description,
            'Trade_Item_GTIN': self.gtin,
            'Information_Provider_GLN': self.gln_of_information_provider or self.get_leading(),
            'Information_Provider_Name': settings.GS1_GEPIR_EXPORT_NAME,
            'Target_Market': self.target_market.code if self.target_market else '372',
            'Base_Unit_Indicator': self.is_bunit,
            'Consumer_Unit_Indicator': self.is_cunit,
            'Variable_Weight_Trade_Item': self.is_vunit,
            'Ordering_Unit_Indicator': self.is_ounit,
            'Dispatch_Unit_Indicator': self.is_dunit,
            'Invoice_Unit_Indicator': self.is_iunit,
            'Start_Availability_Date_Time': self.start_availability,
            'Classification_Category_Code': str(self.category) if self.category else None,
            'Trade_Item_Unit_Descriptor': self.package_level.unit_descriptor if self.package_level else None,
            'Functional_Name': self.functional_name,
            'Brand_Name': self.brand,
            'Packaging_Marked_Returnable': self.returnable,
            'Height': self.height,
            'Height_UOM': self.height_uom.code if self.height_uom else None,
            'Width': self.width,
            'Width_UOM': self.width_uom.code if self.width_uom else None,
            'Depth': self.depth,
            'Depth_UOM': self.depth_uom.code if self.depth_uom else None,
            'Gross_Weight': self.gross_weight,
            'Gross_Weight_UOM': self.gross_weight_uom.code if self.gross_weight_uom else None,
            'End_Availability_Date_Time': self.end_availability,
            'Sub_Brand': self.sub_brand,
            'Brand_Owner_GLN': self.brand_owner_gln,
            'Brand_Owner_Name': self.brand_owner_name,
            'Product_Description': self.description,
            'Variant_Description': self.variant,
            'Packaging_Type_Code': self.package_type.code if self.package_type else None,
            'Trade_Item_Last_Change_Date': self.updated.strftime('%Y-%m-%dT%H:%M:%S'),
            'Discontinued_Date': self.discontinued_date,
            'Trade_Item_Country_Of_Origin': self.country_of_origin.code if self.country_of_origin else None,
            'Manufacturer_GLN': self.manufacturer_gln,
            'Manufacturer_Name': self.manufacturer_name,
            'Is_Price_On_Pack': self.is_price_on_pack,
            'Barcode_Type': internal_bar_type_to_repr(self.bar_type),
            'Additional_Trade_Item_Identification_Type': 'SUPPLIER_ASSIGNED',
            'Additional_Trade_Item_Identification_Value': self.sku,
            # 'Type_Of_Information': 'WEBSITE',
            'Uniform_Resource_Identifier': self.website_url,
            'Trade_Item_Status': 'ADD',
            'GS1CloudStatus': self.gs1_cloud_state,
            'Use_Language_Code_List': self.language.slug if self.language else 'en',
            'Company_Name': self.company if self.company else self.organisation.company
        }
        if data['Trade_Item_Unit_Descriptor'] != 'BASE_UNIT_OR_EACH':
            data.update(
                {
                    'GTIN_Of_Next_Lower_Item': self.gtin_of_next_lower_item,
                    'Amount_Of_Next_Lower_Level_Items': self.total_quantity_of_next,
                    'Quantity_Of_Children': self.quantity_of_children,
                    'Total_Quantity_Of_Next_Lower_Level_Trade_Item': self.total_quantity_of_next
                }
            )
        else:
            data.update(
                {
                    'Net_Content': self.net_content,
                    'Net_Content_UOM': self.net_content_uom.code if self.net_content_uom else None,
                    'Net_Weight': self.net_weight,
                    'Net_Weight_UOM': self.net_weight_uom.code if self.net_weight_uom else None
                }
            )

        # if image url is present, we qualify it as PRODUCT_IMAGE in the export
        if self.website_url:
            data.update(
                {
                    'Type_Of_Information': 'PRODUCT_IMAGE'
                }
            )

        # Dates
        current_ts = datetime.datetime.now()
        if not self.pub_date:
            data.update({'Publication_Date': current_ts, })
        else:
            data.update({'Publication_Date': self.pub_date})
        if not self.eff_date:
            data.update({'Effective_Date': current_ts})
        else:
            data.update({'Effective_Date': self.pub_date})
        if not self.start_availability:
            data.update({'Start_Availability_Date_Time': current_ts})
        else:
            data.update(
                {'Start_Availability_Date_Time': self.start_availability})

        return data

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        original_instance = self.__class__.objects.filter(pk=self.pk).first()
        super().save(force_insert, force_update, using, update_fields)

        # prevent to post updates when in test environment
        if not test_helpers.is_test_environment():
            # we have to compare what is changed in the instance,
            # so original instance must be retrieved from database
            request = CrequestMiddleware.get_request()  # global request
            update_gs1_cloud_product.delay(
                instance=self,
                original_instance=original_instance,
                user=request.user,
                force=False,
            )


class ProductFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(lookup_expr='iexact')
    gtin = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    sku = django_filters.CharFilter(lookup_expr='iexact')
    is_bunit = django_filters.BooleanFilter()
    is_cunit = django_filters.BooleanFilter()
    is_iunit = django_filters.BooleanFilter()

    class Meta:
        model = Product
        fields = ['brand', 'gtin', 'description',
                  'sku', 'is_bunit', 'is_cunit', 'is_iunit']


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='product_images', on_delete=models.CASCADE)
    image = models.ImageField(_('Image'), upload_to=product_helper.image_upload_directory)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    def __unicode__(self):
        return f'Image for {self.product} [{self.language}]'

    def delete(self, using=None, keep_parents=False):
        self.image.delete()
        return super().delete(using, keep_parents)
