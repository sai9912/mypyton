import simplejson as json
from rest_framework import serializers
from rest_framework.fields import empty


class I18nCharField(serializers.CharField):

    @staticmethod
    def is_empty_i18n_data(data):
        """
        check for values in each language
        empty value example: {"en":""}
        """

        if data is empty:
            return True

        return not any(json.loads(data).values())

    def validate_empty_values(self, data):
        """
        Empty i18n fields have the following format: {"en":""},
        we have to decode json and check empty strings for languages
        """

        if self.is_empty_i18n_data(data) and self.required:
            self.fail('required')

        return super().validate_empty_values(data)
