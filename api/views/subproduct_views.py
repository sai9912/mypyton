from knox.auth import TokenAuthentication
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from api.serializers.product_serializers import ProductSerializer
from api.serializers.subproduct_serializer import SubProductSerializer
from member_organisations.models import ProductTemplate
from products.models.product import Product
from products.models.sub_product import SubProduct
from ..filters import ProductsFilterBackend


class SubproductListAPIView(generics.ListAPIView):
    """
    get: Get a Subproducts
    """
    serializer_class = SubProductSerializer
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        # django model translation requires get_queryset method
        # check rest-framework section here:
        # http://django-modeltranslation.readthedocs.io/en/latest/caveats.html
        return SubProduct.objects.all()

    def get(self, request, gtin):
        try:
            product = Product.objects.get(gtin=gtin)
        except:
            return Response({'message': 'Unknown GTIN'}, status=HTTP_400_BAD_REQUEST)

        try:
            queryset = SubProduct.objects.filter(product=product).order_by('sub_product__gtin').all()
            filter_backend = ProductsFilterBackend()
            queryset = filter_backend.filter_queryset(request, queryset, self)
            subproducts = []
            quantities = {}
            for sub_product in queryset:
                subproducts.append(sub_product.sub_product)
                quantities[sub_product.sub_product.gtin] = sub_product.quantity

            serializer = ProductSerializer(subproducts, many=True)
            data = serializer.data
            member_organisation = request.user.profile.member_organisation
            product_templates = ProductTemplate.objects.filter(member_organisation=member_organisation).order_by('order')
            package_levels = dict()
            for product_template in product_templates:
                package_levels[product_template.package_level_id] = product_template.ui_label

            for item in data:
                item['package_level']['ui_level'] = package_levels.get(item['package_level']['value'], '')
                item['quantity'] = quantities[item['gtin']['value']]
        except:
            return Response({'message': 'Invalid request'}, status=HTTP_400_BAD_REQUEST)

        return Response(data)

    def post(self, request, gtin):
        try:
            product = Product.objects.get(gtin=gtin)
        except:
            return Response({'message': 'Unknown product GTIN'}, status=HTTP_400_BAD_REQUEST)

        try:
            sub_product = Product.objects.get(gtin=request.data['subproduct'])
        except:
            return Response({'message': 'Unknown product GTIN'}, status=HTTP_400_BAD_REQUEST)

        try:
            quantity = request.data['quantity']
        except:
            return Response({'quantity': 'This field required'}, status=HTTP_400_BAD_REQUEST)

        subproduct, created = SubProduct.objects.get_or_create(
            product=product,
            sub_product=sub_product
        )
        subproduct.quantity = quantity
        subproduct.save()

        return Response({ 'product': product.gtin,
                          'sub_product': sub_product.gtin,
                          'quantity': subproduct.quantity })


class SubproductCreateListAPIView(generics.ListAPIView):
    """
    get: Get a Subproducts
    """
    serializer_class = SubProductSerializer
    authentication_classes = (TokenAuthentication,)
    # filter_backends = (MOFilterBackend, LangFilterBackend,)

    def get_queryset(self):
        # django model translation requires get_queryset method
        # check rest-framework section here:
        # http://django-modeltranslation.readthedocs.io/en/latest/caveats.html
        return SubProduct.objects.all()

    def get(self, request):
        try:
            session = request.session.get('new_product', None)

            subproducts = []
            for gtin in session.get('sub_products', []):
                try:
                    product = Product.objects.get(gtin=gtin)
                    subproducts.append(product)
                except:
                    pass
        except:
            return Response({'message': 'Product have no subproducts'}, status=HTTP_400_BAD_REQUEST)

        try:
            serializer = ProductSerializer(subproducts, many=True)
            data = serializer.data
            for item in data:
                item['count'] = 1
        except:
            return Response({'message': 'Invalid request'}, status=HTTP_400_BAD_REQUEST)

        return Response(data)


class SubproductRetrieveAPIView(generics.GenericAPIView):
    serializer_class = SubProductSerializer
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return SubProduct.objects.all()

    def get(self, request, *args, **kwargs):    # gtin, subproduct_gtin):
        # get subproduct details
        serializer = SubProductSerializer(data=kwargs)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(e, status=HTTP_400_BAD_REQUEST)

        try:
            subproduct = serializer.get_subproduct()
        except Exception as e:
            return Response({'message': e.args[0]}, status=HTTP_400_BAD_REQUEST)

        sub_product_serializer = ProductSerializer(subproduct.sub_product)
        return Response(sub_product_serializer.data)

    def post(self, request, product, sub_product):
        try:
            quantity = request.data['quantity']
        except:
            return Response({'quantity': 'This field required'}, status=HTTP_400_BAD_REQUEST)

        try:
            product_rec = Product.objects.get(gtin=product)
        except:
            return Response({'product': 'This field required'}, status=HTTP_400_BAD_REQUEST)

        try:
            sub_product_rec = Product.objects.get(gtin=sub_product)
        except:
            return Response({'subproduct': 'This field required'}, status=HTTP_400_BAD_REQUEST)

        try:
            SubProduct.objects.create(product=product_rec,
                                      sub_product=sub_product_rec,
                                      quantity=quantity)
        except:
            return Response({'message': 'Subproduct exist'}, status=HTTP_400_BAD_REQUEST)

        return Response({'product': product_rec.gtin,
                         'sub_product': sub_product_rec.gtin,
                         'quantity': int(quantity)})

    def patch(self, request, *args, **kwargs):
        # change subproduct quantity
        try:
            quantity = request.data['quantity']
        except:
            return Response({'quantity': 'This field required'}, status=HTTP_400_BAD_REQUEST)

        data=kwargs
        data['quantity'] = quantity
        serializer = SubProductSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(e, status=HTTP_400_BAD_REQUEST)

        try:
            subproduct = serializer.get_subproduct()
            subproduct.quantity = quantity
            subproduct.save()
        except Exception as e:
            return Response({'message': e.args[0]}, status=HTTP_400_BAD_REQUEST)

        return Response(data)

    def delete(self, *args, **kwargs):
        # delete subproduct
        serializer = SubProductSerializer(data=kwargs)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(e, status=HTTP_400_BAD_REQUEST)

        try:
            subproduct = serializer.get_subproduct()
            subproduct.delete()
        except Exception as e:
            return Response({'message': e.args[0]}, status=HTTP_400_BAD_REQUEST)

        return Response({'status': 'ok'})
