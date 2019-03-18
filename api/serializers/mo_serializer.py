from rest_framework import serializers

from BCM.models import Country
from member_organisations.models import MemberOrganisation


class MemberOrganisationSerializer(serializers.ModelSerializer):
    """
    Used for MO details retrieving for now, update permissons/allowed methods to enhance features
    """

    country = serializers.SlugRelatedField(
        slug_field='slug', queryset=Country.objects.all(), required=True
    )

    class Meta:
        model = MemberOrganisation
        exclude = (
            'gs1_cloud_username', 'gs1_cloud_secret', 'gs1_cloud_ds_gln', 'users'
        )
