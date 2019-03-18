from knox.auth import TokenAuthentication
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.mixins import CreateModelMixin

from api.permissions import IsOwnerOrMOStaff
from api.serializers.barcode_serializer import (
    BarcodePreviewSerializer, BarcodeGenerateSerializer, BarcodeLabelSerializer
)
from barcodes.models import Label
from products.models import Product


class BarcodeListCreateAPIView(generics.RetrieveAPIView):
    """
    1. a user hasn't confirmed a barcode agreement
        - barcode priview
    2. a user confirmed a barcode agreement
    """

    serializer_class = None
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsOwnerOrMOStaff,)
    queryset = Product.objects.all()
    lookup_url_kwarg = 'gtin'
    lookup_field = 'gtin'
    http_method_names = ('get', 'post', 'head', 'options', )

    # def post(self, request, *args, **kwargs):
    #     return self.create(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        serializers_by_type = {
            # 'type' comes from url kwargs
            'preview': BarcodePreviewSerializer,
            'generate': BarcodeGenerateSerializer,
        }
        kwargs['context'] = self.get_serializer_context()

        # note: some magic is here, we send GET data to serializer
        kwargs['data'] = self.request.GET.dict()
        serializer_class = serializers_by_type.get(self.kwargs.get('type'))

        if serializer_class:
            serializer = serializer_class(*args, **kwargs)
            serializer.is_valid(raise_exception=True)
            return serializer
        else:
            raise NotFound('Wrong barcode request type')


class BarcodeLabelListAPIView(generics.ListAPIView):
    serializer_class = BarcodeLabelSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsOwnerOrMOStaff,)
    queryset = Label.objects.all()
    http_method_names = ('get', 'head', 'options', )
