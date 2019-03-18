from prefixes.actions import export_as_csv_action
from prefixes.admin import RelatedDropdownFilter


class MemberOrganisationCustomMixin:
    """
    Mixin for MemberOrganisationAdmin and MemberOrganisationUserCustomAdmin
    """

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).select_related(
            'country',
        )

    actions = (
        export_as_csv_action(
            'CSV Export',
            fields=[
                'gs1_cloud_username',
                'country__name',
            ],
            all_objects=True
        ),
    )
    list_display = (
        'country_name',
        'gs1_cloud_username',
    )

    @staticmethod
    def country_name(mo):
        return mo.country.name

    search_fields = (
        'gs1_cloud_username',
    )

    list_filter = (
        ('country', RelatedDropdownFilter),
    )
