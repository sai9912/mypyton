from rest_framework.serializers import ValidationError
from django.utils.translation import gettext as _


"""
This validators was tested like so:

    class IntegerSerializer(serializers.Serializer):
        value = serializers.CharField(
            max_length=50,
            validators=[IntegerValidator()]
        )
    serializer = IntegerSerializer(data=dict(value='1'))
    serializer_is_valid = serializer.is_valid()
"""

__all__ = (
    'IntegerValidator',
    'FloatValidator',
    'PositiveFloatValidator',
)


class IntegerValidator:
    serializer_field = None
    serializer_instance = None

    def __init__(self, *args, **kwargs):
        pass

    def set_context(self, serializer_field, *args, **kwargs):
        self.serializer_field = serializer_field
        self.serializer_instance = serializer_field.parent

    def __call__(self, value):
        try:
            int(value)
        except Exception as e:
            raise ValidationError(_('This field must be an integer.'))

    def __repr__(self):
        return str(self.__class__.__name__)


class FloatValidator:
    serializer_field = None
    serializer_instance = None

    def __init__(self, *args, **kwargs):
        pass

    def set_context(self, serializer_field, *args, **kwargs):
        self.serializer_field = serializer_field
        self.serializer_instance = serializer_field.parent

    def __call__(self, value):
        try:
            float(value)
        except Exception as e:
            raise ValidationError(_('This field must be a number.'))

    def __repr__(self):
        return str(self.__class__.__name__)


class PositiveFloatValidator:
    serializer_field = None
    serializer_instance = None

    def __init__(self, *args, **kwargs):
        pass

    def set_context(self, serializer_field, *args, **kwargs):
        self.serializer_field = serializer_field
        self.serializer_instance = serializer_field.parent

    def __call__(self, value):
        try:
            float_value = float(value)
            assert float_value > 0
        except Exception as e:
            raise ValidationError(_('This field must be a positive number.'))

    def __repr__(self):
        return str(self.__class__.__name__)


class GenericUOMValidator:
    """
    This validator is used to detect when UOM was specified without respective value.
    It's possible when a field is marked as "ui_mandatory = False".
    """

    serializer_field = None
    serializer_instance = None

    def __init__(self, *args, **kwargs):
        pass

    def set_context(self, serializer_field, *args, **kwargs):
        self.serializer_field = serializer_field
        self.serializer_instance = serializer_field.parent

    def __call__(self, value):
        uom_field_name = self.serializer_field.field_name

        if uom_field_name.endswith('_uom') and value:
            value_field_name = uom_field_name.split('_uom')[0]
            value_field = self.serializer_instance.fields.get(value_field_name)
            value_field_data = self.serializer_instance.initial_data.get(value_field_name)
            if value_field and not self.serializer_instance.initial_data.get(value_field_name):
                # it's requied to check initial_data here,
                # cause we don't have validated values yet
                raise ValidationError(_('Please specify both value and unit or leave them blank'))
            try:
                float(value_field_data)
            except Exception as e:
                raise ValidationError(_('Value can not be converted to a number'))
            try:
                assert float(value_field_data) > 0
            except Exception as e:
                raise ValidationError(_('Value should be a positive number'))

    def __repr__(self):
        return str(self.__class__.__name__)
