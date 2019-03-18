from django.utils.translation import gettext as _, activate
from rest_framework import serializers


class GPCSerializer(serializers.Serializer):
    """
    Dummy serializer, just for help in swagger
    """

    segment = serializers.CharField(label=_('Segment'))
    segment_code = serializers.IntegerField(label=_('Segment code'))
    # not sure why "ll", source api has it
    familly = serializers.CharField(label=_('Familly'))
    familly_code = serializers.IntegerField(label=_('Familly code'))
    # class is a keyword in python
    class_ = serializers.CharField(label=_('Class'))
    class_code = serializers.IntegerField(label=_('Class code'))
    brick = serializers.CharField(label=_('Brick'))
    brick_code = serializers.IntegerField(label=_('Brick code'))
    attribute = serializers.CharField(label=_('Attribute'))

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
