from rest_framework.serializers import ValidationError

__all__ = (
    'DescriptionValidator',
)


class DescriptionValidator:
    serializer_field = None
    serializer_instance = None

    def __init__(self, *args, **kwargs):
        """
        You can pass additional parameters here from serilizer
        """

        pass

    def set_context(self, serializer_field, *args, **kwargs):
        self.serializer_field = serializer_field
        self.serializer_instance = serializer_field.parent

    def __call__(self, value):
        """
        Actual validation performs here.
        Useful attributes:
            field_name: self.serializer_field.field_name
            initial_data: self.serializer_instance.initial_data

        NOTE: It's impossible to change data here for a field or for a whole model!
              But you have all available data for reading.
        """

        if value == '__test_error__':
            raise ValidationError('Test error for the description field')

    def __repr__(self):
        return str(self.__class__.__name__)
