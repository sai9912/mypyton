from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from member_organisations.models import MemberOrganisationRelation
from prefixes.actions import export_as_csv_action
from prefixes.admin import RelatedDropdownFilter
from products.admin_actions import gs1_cloud_draft_action, gs1_cloud_reactivate_action
from products.models.country_of_origin import CountryOfOrigin
from products.models.dimension_uom import DimensionUOM
from products.models.package_level import PackageLevel
from products.models.package_type import PackageType
from products.models.product import Product, ProductImage
from products.models.net_content_uom import NetContentUOM
from products.models.target_market import TargetMarket
from products.models.language import Language
from products.models.weight_uom import WeightUOM
from utils import RightSideAdminLinkInfo, RightSideLinksAdminMixin


@admin.register(PackageLevel)
class PackageLevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'unit_descriptor', )


@admin.register(PackageType)
class PackageTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'member_organisation', 'ui_enabled')


@admin.register(TargetMarket)
class TargetMarketAdmin(admin.ModelAdmin):
    list_display = ('code', 'market', )


@admin.register(Language)
class TargetMarketAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name',)


class ProductCustomMixin(RightSideLinksAdminMixin):
    actions = (
        export_as_csv_action(
            'CSV Export',
            fields=[
                'gtin',
                'owner',
                'description_i18n',
                'created',
            ],
            all_objects=True,
        ),
        gs1_cloud_draft_action('Force change GS1 cloud state to "DRAFT"', 'DRAFT'),
        gs1_cloud_reactivate_action('Force reactivate products in GS1 cloud'),
    )
    list_display = (
        'gtin',
        'owner',
        'description_i18n',
        'gs1_cloud_state',
        'created',
    )
    search_fields = (
        'gtin',
        'owner__email',
        'company_organisation__uuid',
    )
    list_filter = (
        ('owner', RelatedDropdownFilter),
    )

    right_side_links = [
        RightSideAdminLinkInfo(
            name='owner',
            url='auth/user/{obj.owner_id}/change/'
        ),
        RightSideAdminLinkInfo(
            name='organization',
            url='company_organisations/companyorganisation/'
                '{obj.company_organisation_id}/change'
        ),
        RightSideAdminLinkInfo(
            name='gs1 logs',
            url='audit/cloudlog/?q={obj.gtin}'
        ),
    ]


@admin.register(Product)
class ProductAdmin(ProductCustomMixin, admin.ModelAdmin):
    change_form_template = 'admin/custom_change_view.html'


@admin.register(CountryOfOrigin)
class CountryOfOriginAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'language')
    raw_id_fields = ('product', )


class MemberOrganisationRelationInline(GenericTabularInline):
    model = MemberOrganisationRelation


@admin.register(NetContentUOM)
class NetContentUOMAdmin(admin.ModelAdmin):
    inlines = [MemberOrganisationRelationInline]


@admin.register(DimensionUOM)
class DimensionUOMAdmin(admin.ModelAdmin):
    inlines = [MemberOrganisationRelationInline]


@admin.register(WeightUOM)
class WeightUOMAdmin(admin.ModelAdmin):
    inlines = [MemberOrganisationRelationInline]

