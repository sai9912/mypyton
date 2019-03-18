import coreapi
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Q
from django.utils.translation import gettext as _, activate
from drf_yasg.openapi import Schema
from rest_framework.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend

from BCM.models import Language
from member_organisations.models import MemberOrganisation
from products.models.package_level import PackageLevel


class MOFilterBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='mo',
                location='query',
                required=False,
                description='MemberOrganisation slug',
                type='string',
                example='&mo=gs1belu',
                schema=Schema(
                    description='MemberOrganisation slug',
                    type='string'
                )
            )
        ]

    def validate_mos(self, mos):
        mos_found = MemberOrganisation.objects.filter(slug__in=mos).count()
        if len(mos) > 1:
            raise ValidationError(_('Multiple MOs were specified, please specify only one'))
        if not mos_found:
            raise ValidationError(_('Wrong MO slug specified'))

        return True

    def filter_queryset(self, request, queryset, view):
        mos_param = set(request.query_params.getlist('mo'))

        if mos_param:
            self.validate_mos(mos_param)
            return queryset.filter(member_organisation__slug__in=mos_param)
        else:
            return queryset


class LangFilterBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='lang',
                location='query',
                required=False,
                description='Language slug',
                type='string',
                example='&lang=fr',
                schema=Schema(
                    description='Language slug',
                    type='string'
                )
            )
        ]

    def validate_langs(self, langs):
        langs_found = Language.objects.filter(slug__in=langs).count()
        if len(langs) > 1:
            raise ValidationError(_('Multiple languages were specified, please specify only one'))
        if not langs_found:
            raise ValidationError(_('Wrong language code specified'))

        return True

    def filter_queryset(self, request, queryset, view):
        langs_param = list(set(request.query_params.getlist('lang')))

        if langs_param:
            self.validate_langs(langs_param)
            activate(langs_param[0])  # should be only one language in list here

        return queryset


class GPCBrickFilterBackend(BaseFilterBackend):
    """
    Dummy filter, just for help in swagger
    """

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='brick',
                location='query',
                required=False,
                description='Brick part',
                type='string',
                example='&brick=tele',
                schema=Schema(
                    description='Brick part',
                    type='string'
                )
            ),
            coreapi.Field(
                name='brick_code',
                location='query',
                required=False,
                description='Brick code',
                type='string',
                example='&brick_code=123',
                schema=Schema(
                    description='Brick code',
                    type='string'
                )
            ),
        ]

    def filter_queryset(self, request, queryset, view):
        """
        Dummy method there is no queryset for this api
        """
        return queryset


class ProductsFilterBackend(BaseFilterBackend):
    def filter_list(self, queryset, params, member_organisation):

        # current templates
        all_packaging_levels = [
            ('base', PackageLevel.BASE),
            ('pack', PackageLevel.PACK),
            ('case', PackageLevel.CASE),
            ('pallet', PackageLevel.PALLET),
            ('display_shipper', PackageLevel.DISPLAY_SHIPPER),
        ]

        # MO's templates
        if member_organisation:
            available_package_levels = [t.package_level.id for t in member_organisation.product_templates.all()]
        else:
            available_package_levels = [o for s, o in all_packaging_levels]

        # exclude everything MO does not have or user does not tick
        for s, o in all_packaging_levels:
            if o in available_package_levels:
                # MO has such template listed
                if not int(params.get(s, 1)):
                    queryset = queryset.exclude(package_level_id=o)
                pass
            else:
                # MO has no such template listed
                queryset = queryset.exclude(package_level_id=o)

        if params.get('brand', None):
            queryset = queryset.filter(brand_i18n__icontains=params.get('brand', None))

        if params.get('gtin', None):
            queryset = queryset.filter(gtin__icontains=params.get('gtin', None))

        if params.get('description', None):
            queryset = queryset.filter(description_i18n__icontains=params.get('description', None))

        if params.get('sku', None):
            queryset = queryset.filter(sku__icontains=params.get('sku', None))

        if params.get('mark', None):
            queryset = queryset.filter(mark=1)

        if params.get('target_market', None):
            queryset = queryset.filter(target_market__code=params.get('target_market', None))

        if params.get('search', None):
            query = Q(brand_i18n__icontains=params.get('search', None))
            query.add(Q(gtin__icontains=params.get('search', None)), Q.OR)
            query.add(Q(description_i18n__icontains=params.get('search', None)), Q.OR)
            query.add(Q(sku__icontains=params.get('search', None)), Q.OR)
            queryset = queryset.filter(query)

        if params.get('prefix', None):
            queryset = queryset.filter(gs1_company_prefix=params.get('prefix', None))

        return queryset

    def filter_queryset(self, request, queryset, view):
        queryset = self.filter_list(queryset, request.query_params, request.user.profile.member_organisation)

        page = request.query_params.get('page', None)
        products_per_page = request.query_params.get('products_per_page', settings.PRODUCTS_PER_PAGE)

        paginator = Paginator(queryset, products_per_page)
        try:
            paginator_page = paginator.page(page)
        except InvalidPage:
            paginator_page = paginator.page(1)

        view.pagination_numpage = paginator_page.number
        view.pagination_numpages = paginator.num_pages
        view.pagination_hasprev = paginator_page.has_previous()
        view.pagination_hasnext = paginator_page.has_next()

        queryset = paginator_page.object_list
        return queryset
