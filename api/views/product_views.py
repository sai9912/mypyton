from django.db.models import Q
from knox.auth import TokenAuthentication
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from api.permissions import IsOwnerOrMOStaff
from api.serializers.product_serializers import ProductSerializer, ProductTemplateDetailsSerializer, \
    ProductWithSubProductsSerializer
from api.serializers.product_serializers import ProductTemplateSerializer
from api.serializers.product_serializers import ProductPackagingSerializer
from api.serializers.product_serializers import SubProductSerializer
from api.filters import MOFilterBackend, LangFilterBackend
from member_organisations.models import ProductTemplate, ProductPackaging
from products.models.product import Product
from products.models.sub_product import SubProduct
from products.models.country_of_origin import CountryOfOrigin
from products.models.target_market import TargetMarket

from services import country_of_origin_service, target_market_service, language_service
from .generic_views import GenericBCMViews
from ..filters import ProductsFilterBackend


class ProductsListCreateAPIView(GenericBCMViews, generics.ListCreateAPIView):
    """
    get: List all Products for the given company
    post: Create Product for the given company
    """
    serializer_class = ProductSerializer
    filter_backends = (ProductsFilterBackend,)
    pagination_numpage = 0
    pagination_numpages = 0
    pagination_hasprev = 0
    pagination_hasnext = 0

    def get_product_template(self):
        """
        Returns product template if it's specified explicitly by template_name
        :return:
        """

        template_name = self.request.query_params.get('template_name')
        if template_name:
            return ProductTemplate.objects.filter(name=template_name).first()

    def get_serializer(self, *args, **kwargs):
        product_template = self.get_product_template()
        if product_template:
            kwargs['product_template'] = product_template
        return self.serializer_class(context={'request': self.request}, *args, **kwargs)

    def get_queryset(self):
        """
        Query Prefixes by logged User's company
        If company does not exist return 404
        """
        if self.user_type_query:
            return Product.objects.filter(**self.user_type_query)
        return Product.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = Product.objects.all()
        order = request.query_params.get('order','gtin')
        if request.query_params.get('is_desc', 'true') == 'true':
                order = '-' + order

        queryset = queryset.order_by(order)
        filter_backend = ProductsFilterBackend()
        queryset = filter_backend.filter_queryset(request, queryset, self)
        serializer = ProductWithSubProductsSerializer(queryset, many=True)

        products = serializer.data
        return Response({'products': products,
                         'pagination_numpage': self.pagination_numpage,
                         'pagination_numpages': self.pagination_numpages,
                         'pagination_hasprev': self.pagination_hasprev,
                         'pagination_hasnext': self.pagination_hasnext})


class ProductRetrieveAPIView(GenericBCMViews, generics.RetrieveUpdateDestroyAPIView):
    """
    get: Retrieve the given Product
    patch: Partial update given Product (Means that does not require any required fields)
    put: Fully update given Product (Means that require all the required fields even those that already was filled)
    delete: Delete the given Product
    """

    serializer_class = ProductSerializer
    lookup_field = 'gtin'

    def get_product_template(self):
        """
        Returns product template if it's specified explicitly by template_name
        :return:
        """

        template_name = self.request.query_params.get('template_name')
        if template_name and template_name != 'null':
            return ProductTemplate.objects.filter(name=template_name).first()

        template_id = self.request.query_params.get('template_id')
        if template_id and template_id != 'null':
            return ProductTemplate.objects.filter(id=template_id).first()

    def get_serializer(self, *args, **kwargs):
        product_template = self.get_product_template()
        if product_template:
            kwargs['product_template'] = product_template
        return self.serializer_class(context={'request': self.request}, *args, **kwargs)

    def get_queryset(self):
        """
        Query Prefixes by logged User's company
        If company does not exist return 404
        """
        if self.user_type_query:
            return Product.objects.filter(**self.user_type_query)
        return Product.objects.all()


class ProductWithPrefixListCreateAPIView(GenericBCMViews, generics.ListCreateAPIView):
    """
    get: Retrieve all Products for teh given Prefix
    post: Create Product for the given Prefix
    """
    queryset = Product.objects.all()
    lookup_field = 'gs1_company_prefix'
    lookup_url_kwarg = 'prefix'
    serializer_class = ProductSerializer

    def get_product_template(self):
        """
        Returns product template if it's specified explicitly by template_name
        :return:
        """

        template_name = self.request.query_params.get('template_name')
        if template_name:
            return ProductTemplate.objects.filter(name=template_name).first()

    def get_serializer(self, *args, **kwargs):
        product_template = self.get_product_template()
        if product_template:
            kwargs['product_template'] = product_template
        return self.serializer_class(context={'request': self.request}, *args, **kwargs)

    def get_queryset(self):
        """
        List all Products for the given Prefix
        If Prefix does not exist return 404
        """
        prefix = self.kwargs.get(self.lookup_url_kwarg)
        return Product.objects.filter(gs1_company_prefix=prefix)

    def create(self, request, *args, **kwargs):
        # request.data['gs1_company_prefix'] = self.kwargs.get(self.lookup_url_kwarg)
        return super(ProductWithPrefixListCreateAPIView, self).create(request, *args, **kwargs)


class ProductTemplateListAPIView(generics.ListCreateAPIView):
    """
    get: Get a filtered list of ProductTemplates ('mo', 'lang' query parameters)
    """
    serializer_class = ProductTemplateSerializer
    http_method_names = ['get', 'head', 'options']
    authentication_classes = (TokenAuthentication,)
    filter_backends = (MOFilterBackend, LangFilterBackend,)

    def get_queryset(self):
        # django model translation requires get_queryset method
        # check rest-framework section here:
        # http://django-modeltranslation.readthedocs.io/en/latest/caveats.html
        return ProductTemplate.objects.all()


class ProductTemplateRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    queryset = ProductTemplate.objects.all()
    authentication_classes = (TokenAuthentication, )
    serializer_class = ProductTemplateDetailsSerializer

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(context={"request": self.request}, *args, **kwargs)


class ProductPackagingListAPIView(generics.ListAPIView):
    """
    get: Get a filtered list of ProductPackagings ('mo', 'lang' query parameters)
    """
    serializer_class = ProductPackagingSerializer
    http_method_names = ['get', 'head', 'options']
    authentication_classes = (TokenAuthentication,)
    filter_backends = (MOFilterBackend, LangFilterBackend,)

    def get_queryset(self):
        # django model translation requires get_queryset method
        # check rest-framework section here:
        # http://django-modeltranslation.readthedocs.io/en/latest/caveats.html
        return ProductPackaging.objects.all()


class ProductDefaultsListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get(self, request, **kwargs):
        try:
            country = request.user.profile.company_organisation.country
        except AttributeError:
            country = None

        language_slug = request.user.profile.language
        language = language_service.find_by_slug(language_slug)
        country_of_origin = country_of_origin_service.find_by_country(country)
        target_market = target_market_service.find_by_country(country)

        # FIXME -- default to Belgium(21) for GO users that we could not resolve
        if request.user.profile.member_organisation.name == 'GS1 GO':
            if not country_of_origin:
                country_of_origin = CountryOfOrigin.objects.get(id=21)
            if not target_market:
                target_market = TargetMarket.objects.get(id=21)

        return Response({
            'country_of_origin': getattr(country_of_origin, 'id', None),
            'target_market': getattr(target_market, 'id', None),
            'language': getattr(language, 'id', None),
        })


class ProductCloneAPIView(generics.GenericAPIView):
    serializer_class = SubProductSerializer
    authentication_classes = (TokenAuthentication,)
    # filter_backends = (MOFilterBackend, LangFilterBackend,)

    def get_queryset(self):
        # django model translation requires get_queryset method
        # check rest-framework section here:
        # http://django-modeltranslation.readthedocs.io/en/latest/caveats.html
        return SubProduct.objects.all()

    def post(self, request):
        gtin = request.data['subproduct_gtin']
        try:
            product = Product.objects.get(gtin=gtin)
            product.gs1_cloud_state = 'DRAFT'
            product.save()
        except:
            return Response({'message': 'Invalid gtin'}, status=HTTP_400_BAD_REQUEST)

        newproduct_gtin = request.data['newproduct_gtin']
        package_level_id = request.data['package_level']

        product.gtin = newproduct_gtin
        product.package_level_id = package_level_id
        product.id = None
        product.save()

        sub_product = Product.objects.get(gtin=gtin)

        SubProduct.objects.create(product=product,
                                  sub_product=sub_product,
                                  quantity=1)

        return Response({'product_id': product.id})

    def _getValid(self, nums):
        """
        Redeclared here due to cyclic import
        """
        if not nums:
            return None

        cd1 = nums[-1]
        meat = nums[0:-1][::-1]  # cut cd away, reverse string, since x3 always applays from right (BC)
        odds = sum(map(lambda i: int(i) * 3, list(meat[0::2])))
        evns = sum(map(lambda i: int(i), list(meat[1::2])))
        cd2 = str(10 - ((odds + evns) % 10))[-1]  # 0 if 10 or reminder
        return nums[0:-1] + cd2

    def put(self, request):
        if not request.user.is_authenticated:
            return Response(status=401)

        gtin = request.data['gtin']
        gtin = self._getValid(gtin)
        try:
            product = Product.objects.get(gtin=gtin)
            base_package_level = product.package_level_id
        except:
            base_package_level = 70

        member_organisation = request.user.profile.member_organisation
        product_templates = ProductTemplate.objects.filter(
            member_organisation=member_organisation
        ).order_by('order')
        templates = list()
        for product_template in product_templates:
            if product_template.package_level_id >= base_package_level:
                continue
            templates.append({'id': product_template.package_level_id,
                              'ui_label': product_template.ui_label})

        existed = []
        for i in range(0, 10):
            check_gtin = self._getValid(str(i) + gtin[1:])
            try:
                Product.objects.get(gtin=check_gtin)
                existed.append(1)
            except:
                existed.append(0)

        return Response({'existed': existed,
                         'templates': templates})
