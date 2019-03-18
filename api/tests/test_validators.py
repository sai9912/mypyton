from rest_framework import serializers
from test_plus import TestCase

from ..validators import (
    FloatValidator,
    PositiveFloatValidator,
    IntegerValidator,
    DescriptionValidator
)


class ValidatorTestCase(TestCase):

    def test_float_serializer(self):
        data = [
            # value is_valid
            ('1', True),
            ('1.2', True),
            ('-1.2', True),
            ('qwe', False),
        ]

        serializer_class = self.create_serializer_class(FloatValidator)
        error_message = 'This field must be a number.'

        self.do_tests(
            data=data,
            serializer_class=serializer_class,
            error_message=error_message
        )

    def test_positive_float_serializer(self):
        data = [
            # value is_valid
            ('1', True),
            ('1.2', True),
            # ('-1.2', False),
            ('qwe', False),
        ]

        error_message = 'This field must be a positive number.'
        serializer_class = self.create_serializer_class(PositiveFloatValidator)

        self.do_tests(
            data=data,
            serializer_class=serializer_class,
            error_message=error_message
        )

    def test_integer_serializer(self):
        data = [
            # value is_valid
            ('1', True),
            ('1.2', False),
            ('-1.2', False),
            ('qwe', False),
        ]

        error_message = 'This field must be an integer.'
        serializer_class = self.create_serializer_class(IntegerValidator)

        self.do_tests(
            data=data,
            serializer_class=serializer_class,
            error_message=error_message
        )

    def test_description_validators(self):
        data = [
            ('some description', True),
            ('another description', True),
            ('__test_error__', False),
        ]
        error_message = 'Test error for the description field'
        serializer_class = self.create_serializer_class(DescriptionValidator)

        self.do_tests(
            data=data,
            serializer_class=serializer_class,
            error_message=error_message
        )

    @staticmethod
    def create_serializer_class(validator):
        assert repr(validator()) == validator.__name__, repr(validator())
        serializer_class = type(
            'Serializer',
            (serializers.Serializer,),
            {'value': serializers.CharField(
                max_length=50,
                validators=[validator()]
            )}
        )

        return serializer_class

    @staticmethod
    def do_tests(data, serializer_class, error_message):

        for value, is_valid in data:
            serializer = serializer_class(data=dict(value=value))
            serializer_is_valid = serializer.is_valid()
            assert serializer_is_valid == is_valid, (serializer.errors, value)
            if not serializer_is_valid:
                assert serializer.errors == {'value': [error_message]}
