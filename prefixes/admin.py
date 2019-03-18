# Register your models here.

from django.contrib import admin
from django.contrib.admin import RelatedFieldListFilter

from utils import RightSideLinksAdminMixin, RightSideAdminLinkInfo
from .models import Prefix, PrefixStatus

from .actions import export_as_csv_action


class RelatedDropdownFilter(RelatedFieldListFilter):
    template = 'admin/drop_down_filters.html'


class PrefixCustomMixin(RightSideLinksAdminMixin):
    list_display = (
        'prefix',
        'company_organisation',
        'member_organisation',
        'status',
    )
    search_fields = (
        'prefix',
        'company_organisation__uuid',
        'company_organisation__name',
    )
    list_filter = (
        ('member_organisation', RelatedDropdownFilter),
    )

    actions = (
        export_as_csv_action(
            'CSV Export',
            fields=[
                'id',
                'prefix',
                'created',
                'company_organisation__uuid',
            ],
            all_objects=True
        ),
    )
    right_side_links = [
        RightSideAdminLinkInfo(
            name='organization',
            url='company_organisations/companyorganisationuser/'
                '{obj.company_organisation_id}/change'
        )
    ]


@admin.register(Prefix)
class PrefixAdmin(PrefixCustomMixin, admin.ModelAdmin):
    change_form_template = 'admin/custom_change_view.html'


@admin.register(PrefixStatus)
class PrefixStatusAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_display_links = ('name',)
