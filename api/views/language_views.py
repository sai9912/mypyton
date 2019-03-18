from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.product_serializers import ProductCountryOfOriginSerializer
from api.serializers.product_serializers import ProductDimensionUOMSerializer
from api.serializers.product_serializers import ProductLanguageSerializer
from api.serializers.product_serializers import ProductNetContentUOMSerializer
from api.serializers.product_serializers import ProductTargetMarketSerializer
from api.serializers.product_serializers import ProductWeightUOMSerializer
from api.utils import get_generic_filtered_queryset
from products.models.country_of_origin import CountryOfOrigin

import django.utils.translation as trans

from products.models.dimension_uom import DimensionUOM
from products.models.weight_uom import WeightUOM
from products.models.net_content_uom import NetContentUOM

from products.models.language import Language
from products.models.target_market import TargetMarket


class LanguageListAPIView(generics.ListAPIView):
    """
    get: Get a list of languages
    """

    serializer_class = ProductLanguageSerializer
    http_method_names = ['get']

    def get_queryset(self):
        return Language.objects.all()

    def list(self, request, *args, **kwargs):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = ProductLanguageSerializer(queryset, many=True)
        return Response(serializer.data)


class LanguageUIListAPIView(APIView):
    """
    get: Get a list of UI languages
    """

    serializer_class = ProductLanguageSerializer
    http_method_names = ['get','post']

    def get(self, request, *args, **kwargs):
        try:
            country = request.user.profile.member_organisation.country
            language_by_country = country.languagebycountry_set.order_by('-default', 'language')
            languages = [item.language for item in language_by_country]
        except:  # AttributeError:
            # GO admin might not have MO set, so no country
            languages = Language.objects.all()
        else:
            if not (language_by_country and language_by_country.first().default):
                # we have a default language for a country
                english = [language for language in languages if language.slug == 'en']
                if english:
                    languages = english + [language for language in languages if language.slug != 'en']

        serializer = ProductLanguageSerializer(languages, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        language_slug = request.data['new_language']
        trans.activate(language_slug)
        request.session[trans.LANGUAGE_SESSION_KEY] = language_slug
        request.session['pref_language'] = language_slug
        user = request.user
        user.profile.language = request.data['new_language']
        user.profile.save()
        return Response(language_slug)


class COOListAPIView(generics.ListAPIView):
    """
    get: Get a list of languages
    """

    serializer_class = ProductCountryOfOriginSerializer
    http_method_names = ['get']

    def get_queryset(self):
        return CountryOfOrigin.objects.all()

    def list(self, request, *args, **kwargs):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = ProductCountryOfOriginSerializer(queryset, many=True)
        return Response(serializer.data)


class TMListAPIView(generics.ListAPIView):
    """
    get: Get a list of languages
    """

    serializer_class = ProductTargetMarketSerializer
    http_method_names = ['get']

    def get_queryset(self):
        return TargetMarket.objects.all()

    def list(self, request, *args, **kwargs):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = ProductTargetMarketSerializer(queryset, many=True)
        return Response(serializer.data)


class ProductDimensionUOMView(generics.ListAPIView):
    """
    get: Get a list of dimension UOMs
    """

    serializer_class = ProductDimensionUOMSerializer
    http_method_names = ['get']

    def get_queryset(self):
        return get_generic_filtered_queryset(
            self.serializer_class.Meta.model,
            self.request.user
        )

    def list(self, request, *args, **kwargs):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = ProductDimensionUOMSerializer(queryset, many=True)
        return Response(serializer.data)


class ProductWeightsUOMView(generics.ListAPIView):
    """
    get: Get a list of weight UOMs
    """

    serializer_class = ProductWeightUOMSerializer
    http_method_names = ['get']

    def get_queryset(self):
        return get_generic_filtered_queryset(
            self.serializer_class.Meta.model,
            self.request.user
        )

    def list(self, request, *args, **kwargs):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = ProductWeightUOMSerializer(queryset, many=True)
        return Response(serializer.data)


class ProductNetContentUOMView(generics.ListAPIView):
    """
    get: Get a list of net content UOMs

    """

    serializer_class = ProductNetContentUOMSerializer
    http_method_names = ['get']

    def get_queryset(self):
        return get_generic_filtered_queryset(
            self.serializer_class.Meta.model,
            self.request.user
        )

    def list(self, request, *args, **kwargs):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = ProductNetContentUOMSerializer(queryset, many=True)
        return Response(serializer.data)
