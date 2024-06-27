import logging
import tldextract

from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from size_estimator.estimator import get_size

from customers.models import Customer, CustomerAnalytic, CustomerMeasurement
from customers.serializers import (
    AnalyticInputSerializer,
    AnalyticOutputSerializer,
    AnalyticStatSerializer,
    AnalyticUpdateSerializer,
    CustomerMeasurementSerializer,
)
from products.models import (
    Product,
    ProductAttribute,
    ProductCategoryAttribute,
    ProductSize,
    ProductSizeVendor,
    ProductVendor,
)
from vendors.models import Vendor

logger = logging.getLogger(__name__)


class CustomerAnalyticViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    List all customer analytics, or create a new one.
    """

    vendor = None
    queryset = CustomerAnalytic.objects.all()
    http_method_names = ["post", "get", "patch"]

    def get_serializer_class(self):
        if self.action == "partial_update":
            return AnalyticUpdateSerializer
        return AnalyticInputSerializer

    def create(self, request):
        vendor_url = request.headers.get("Vendor") or request.META["REMOTE_ADDR"]

        try:
            vendor = Vendor.objects.get(shop_url=vendor_url)
        except Vendor.DoesNotExist:
            logger.error(f"Vendor  with domain {vendor_url} does not exist")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            product_vendor = ProductVendor.objects.get(
                external_id=request.data["product"], vendor=vendor
            )
        except ProductVendor.DoesNotExist:
            logger.error(
                f'Product Vendor  with external id {request.data["product"]} does not exist'
            )
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Find product measurements
        product = product_vendor.product

        # TODO: Must get ProductSizeVendor.ProductSize
        sizes = ProductSize.objects.filter(
            product=product.id,
            composed=False,
            productsizevendor__vendor=vendor,
        )
        prod_attrs = {}
        inseam_attrs = {}
        key_metrics = []
        for size in sizes:
            attrs = ProductAttribute.objects.filter(product_size_id=size.id).values(
                "computed_value", "priority", "tag", "value"
            )
            size_attrs = {}
            size_attrs_flag = False
            for attr in attrs:
                if attr["tag"] == "inseam":
                    inseam_attrs[size.display_size] = attr["value"]
                else:
                    size_attrs[attr["tag"]] = attr["computed_value"]
                    size_attrs_flag = True
                    if attr["priority"] == 1 and attr["tag"] not in key_metrics:
                        key_metrics.append(attr["tag"])

            if size_attrs_flag:
                prod_attrs[size.display_size] = size_attrs
        # Only some pants have multiple key metrics
        if (
            len(key_metrics) == 3
            and key_metrics.sort() == ["waist", "hips", "thigh"].sort()
        ):
            cat_tags = ["waist_hips_thigh"]
        else:
            cat_tags = [key_metrics[0]]

        # Find product categorie attributes
        prod_cat_attrs = ProductCategoryAttribute.objects.filter(
            category=product.category, name__in=cat_tags
        ).values("bust", "hips", "thigh", "shift", "waist")
        prod_cat_attrs_list = [attr for attr in prod_cat_attrs]

        # Find customer measurements
        # TODO: CustomerMeasurement should be unique
        customer_measurement = CustomerMeasurement.objects.filter(
            pk=request.data["measurement"]
        )
        cust_meas = customer_measurement.values(
            "bust", "hips", "thigh", "waist", "inseam"
        )[0]

        # Run the estimator
        size = get_size(cust_meas, prod_attrs, prod_cat_attrs_list)

        # TODO: Move inseam computing into estimator lib
        if product.inseam:
            gender = product.gender
            if cust_meas.get("inseam"):
                reco_inseam_meas = None
                reco_inseam = None
                inseams = []
                for key, value in inseam_attrs.items():
                    inseams.append(value)

                # TODO: Order inseams
                user_inseam = cust_meas["inseam"]

                for inseam in inseams:
                    if gender and gender == "women" and inseam >= user_inseam + 5:
                        reco_inseam_meas = inseam
                        break

                if not reco_inseam_meas:
                    absolute_diff = lambda list_value: abs(list_value - user_inseam)
                    reco_inseam_meas = min(inseams, key=absolute_diff)

                for k, v in inseam_attrs.items():
                    if v == reco_inseam_meas:
                        reco_inseam = k
                # TODO: Remove hard code
                if vendor.shop_url == "https://www.goodsociety.org":
                    size = f"{size}/{reco_inseam}"
                else:
                    size = f"{size} / {reco_inseam}"
            else:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error": "missing customer inseam"},
                )

        product_size_vendor = None
        if size:
            product_size = ProductSize.objects.get(product=product, display_size=size)
            result = {"size": size}
            print(product_vendor)

            try:
                # TODO: All ProductSizeVendor must have a ProductVendor associated
                product_size_vendor = ProductSizeVendor.objects.get(
                    product_vendor=product_vendor,
                    product_size=product_size,
                )
                print(product_size_vendor)
                if product_size_vendor.name:
                    result["name"] = product_size_vendor.name
                if product_size_vendor.external_id:
                    result["external_id"] = product_size_vendor.external_id
            except (
                ProductSizeVendor.DoesNotExist,
                ProductSizeVendor.MultipleObjectsReturned,
            ):
                pass

            # TODO: Customer analytic should be unique
            customer_analytics = CustomerAnalytic.objects.filter(
                product_vendor=product_vendor,
                size=product_size,
                measurement=customer_measurement.first(),
            )
            if customer_analytics:
                customer_analytic = customer_analytics[0]
            else:
                customer_analytic = CustomerAnalytic.objects.create(
                    product=product,
                    product_vendor=product_vendor,
                    size=product_size,
                    measurement=customer_measurement.first(),
                )
        else:
            result = {"size": "no match"}
            customer_analytics = CustomerAnalytic.objects.filter(
                product_vendor=product_vendor,
                size__isnull=True,
                measurement=customer_measurement.first(),
            )
            # TODO: Customer analytic should be unique
            if customer_analytics:
                customer_analytic = customer_analytics[0]
            else:
                customer_analytic = CustomerAnalytic.objects.create(
                    product=product,
                    measurement=customer_measurement.first(),
                    product_size_vendor=product_size_vendor,
                    product_vendor=product_vendor,
                )

        result["id"] = customer_analytic.id

        return Response(result)

    # TODO: to remove after all customers on new Shopify app
    def list(self, request, *args, **kwargs):
        try:
            vendor = Vendor.objects.get(shop_url=request.headers.get("Vendor"))
        except Vendor.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        productvendor = ProductVendor.objects.filter(vendor=vendor).values("product_id")
        products = Product.objects.filter(id__in=productvendor)

        queryset = CustomerAnalytic.objects.filter(product__in=products)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AnalyticStatSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AnalyticStatSerializer(queryset, many=True)

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        try:
            analytic = CustomerAnalytic.objects.get(id=kwargs.get("pk"))
        except CustomerAnalytic.DoesNotExist:
            return Response(
                {"error": "no matching analytic"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        logger.debug(serializer.data)
        if serializer.data["size"] == analytic.size.size.name:
            if serializer.data.get("added_to_cart"):
                analytic.added_to_cart = True
            if serializer.data.get("purchased"):
                analytic.purchased = True
        # TODO: Replace by size foreign key when all variants has and external id
        # For now it's not the case for composed sizes
        if serializer.data.get("size_added_to_cart_id"):
            analytic.size_added_to_cart_id = serializer.data["size_added_to_cart_id"]
        if serializer.data.get("added_to_cart_product_title"):
            analytic.added_to_cart_product_title = serializer.data[
                "added_to_cart_product_title"
            ]
        if serializer.data.get("purchased_size_id"):
            analytic.purchased_size_id = serializer.data["purchased_size_id"]
        if serializer.data.get("purchased_product_title"):
            analytic.purchased_product_title = serializer.data[
                "purchased_product_title"
            ]
        analytic.save()

        return Response(status=status.HTTP_200_OK)


class CustomerMeasurementViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    List all customer measurements, or create a new one.
    """

    queryset = CustomerMeasurement.objects.all()
    serializer_class = CustomerMeasurementSerializer
    http_method_names = ["post", "get"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        measurement = serializer.save()

        headers = self.get_success_headers(serializer.data)

        return Response(
            {"id": measurement.id}, status=status.HTTP_201_CREATED, headers=headers
        )

    # TODO: to remove after all customers on new Shopify app
    def list(self, request, *args, **kwargs):
        try:
            vendor = Vendor.objects.get(shop_url=request.headers.get("Vendor"))
        except Vendor.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        productvendor = ProductVendor.objects.filter(vendor=vendor).values("product_id")
        products = Product.objects.filter(id__in=productvendor)

        measurement_ids = CustomerAnalytic.objects.filter(
            product__in=products
        ).values_list("measurement_id", flat=True)

        queryset = CustomerMeasurement.objects.filter(pk__in=measurement_ids)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class CustomerDeleteViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Shopify GDPR webhook
    """

    permission_classes = (AllowAny,)

    # TODO: Process the data deletion request
    def create(self, request, *args, **kwargs):
        return Response()


class CustomerAccessViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Shopify GDPR webhook
    """

    permission_classes = (AllowAny,)

    # TODO: Process the data reading request
    def create(self, request, *args, **kwargs):
        return Response()
