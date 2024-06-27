from rest_framework import generics, mixins, status, viewsets
from rest_framework.response import Response

from products.models import ProductSizeVendor, ProductVendor

from .models import OrderLine
from .serializers import OrderLineSerializer


class OrderViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    lookup_field = "external_id"
    lookup_value_regex = "[a-zA-Z0-9/:]+"
    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer

    def _create_order(self, payload, product_vendor):

        product_size_vendor = None
        try:
            product_size_vendor = ProductSizeVendor.objects.get(
                external_id=payload.get("product_size_vendor")
            )
        except ProductSizeVendor.DoesNotExist:
            pass

        order = OrderLine.objects.create(
            external_id=payload.get("external_id"),
            order_external_id=payload.get("order_external_id"),
            product_vendor=product_vendor,
            amount=payload.get("amount"),
            product_size_vendor_id=product_size_vendor,
            customer_analytic_id=payload.get("customer_analytic"),
        )

        return order

    def create(self, request):
        if isinstance(request.data, list):
            for item in request.data:
                product_vendor_external_id = item.get("product_vendor")
                if product_vendor_external_id:
                    try:
                        product_vendor = ProductVendor.objects.get(
                            external_id=product_vendor_external_id
                        )
                    except ProductVendor.DoesNotExist:
                        pass

                    self._create_order(item, product_vendor)
                else:
                    return Response(
                        {"errors": "no product vendor"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return Response(
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response({"error": "not a list"}, status=status.HTTP_400_BAD_REQUEST)
