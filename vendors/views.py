import json
import logging
import operator
from datetime import datetime
from statistics import mean, median

from django.db.models.functions import Lower
from django.utils.timezone import make_aware
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from customers.models import CustomerAnalytic
from customers.serializers import AnalyticStatSerializer
from products.models import ProductVendor

from .dashboard_views import VendorDashboardViewSet
from .mixins import ReadWriteSerializerMixin
from .models import Vendor, Visit
from .serializers import VendorReadSerializer, VendorWriteSerializer

logger = logging.getLogger(__name__)


class VendorViewSet(
    VendorDashboardViewSet,
    ReadWriteSerializerMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Read and Update vendor info from Shopify app
    """

    read_serializer_class = VendorReadSerializer
    write_serializer_class = VendorWriteSerializer
    queryset = Vendor.objects.all()

    def __get_product_types(self, vendor):
        """
        Returns vendor's products categories and genders to populate Shopify app filters.
        """
        product_vendors = ProductVendor.objects.filter(vendor=vendor)
        genders = (
            product_vendors.annotate(genders=Lower("product__gender"))
            .values_list("genders", flat=True)
            .distinct()
        )
        external_categories = (
            product_vendors.annotate(categories=Lower("external_category"))
            .values_list("categories", flat=True)
            .distinct()
        )

        return {"genders": genders, "external_categories": external_categories}

    def list(self, request, *args, **kwargs):
        """
        Returns vendor's info from Shopify app.
        """
        try:
            vendor = self.get_vendor(request)
        except Exception as error:
            return Response(
                data={"error": str(error)}, status=status.HTTP_404_NOT_FOUND
            )
        product_types = self.__get_product_types(vendor)
        vendor_info = {
            "scircula_plan": vendor.scircula_plan,
            "currency": vendor.currency,
            "integrated_at": vendor.integrated_at,
            "button_url": vendor.button_url,
            "id": vendor.id,
            "script_external_id": vendor.script_external_id,
            "shopify_subscription_id": vendor.shopify_subscription_id,
            "legacy": vendor.legacy,
            "integration_to_be_paid": vendor.integration_to_be_paid,
        }
        vendor_data = {**vendor_info, **product_types}

        return Response(data=vendor_data)

    def partial_update(self, request, *args, **kwargs):
        """
        Updates vendor's info from Shopify app.
        """
        try:
            vendor = self.get_vendor(request)
        except Exception as error:
            return Response(
                data={"error": str(error)}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(vendor, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class VendorDeleteViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Shopify GDPR webhook
    """

    permission_classes = (AllowAny,)

    # TODO: Process the data deletion request
    def create(self, request, *args, **kwargs):
        return Response()


# TODO: to remove after all customers on new Shopify app
class VendorAccessViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Save vendor access log
    """

    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        vendor_url = request.META.get("HTTP_ORIGIN") or request.META.get("HTTP_VENDOR")
        vendor = None
        try:
            vendor = Vendor.objects.get(url=vendor_url)
        except Vendor.DoesNotExist:
            logger.warning(f"Vendor with url {vendor_url} does not exist")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        body_unicode = request.body.decode("utf-8")
        body_data = json.loads(body_unicode)
        logger.debug(body_data)
        access_token = body_data.get("access_token")
        vendor.access_token = bytes(access_token, encoding="utf8")
        vendor.last_logged = make_aware(datetime.now())
        vendor.save()

        return Response(status=status.HTTP_200_OK)


class VendorVisitCreateViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    Save vendor website visits
    """

    permission_classes = (AllowAny,)
    permission_classes_by_action = {"create": [AllowAny], "list": [IsAuthenticated]}

    # TODO: to remove after list method is deleted.
    def get_permissions(self):
        try:
            # Return permission_classes depending on `action`
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except KeyError:
            # Action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    # TODO: How to protect this endpoint?
    def create(self, request, *args, **kwargs):
        vendor_url = request.data.get("location") or request.META.get("HTTP_ORIGIN")
        vendor = None
        try:
            vendor = Vendor.objects.get(shop_url=vendor_url)
        except Vendor.DoesNotExist:
            logger.warning(f"Vendor with url {vendor_url} does not exist")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        Visit.objects.create(
            vendor=vendor, returning=request.data.get("returning") == "true"
        )

        return Response(status=status.HTTP_201_CREATED)

    # TODO: to remove after all customers on new Shopify app
    # and don't forget to also update permissions : remove get_permissions method.
    def list(self, request, *args, **kwargs):
        try:
            vendor = Vendor.objects.get(shop_url=request.headers.get("Vendor"))
        except Vendor.DoesNotExist:
            logger.warning(f"Vendor link to user {request.user} does not exist")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Total number of visits
        visits_count = Visit.objects.filter(vendor=vendor).count()

        return Response(data={"count": visits_count}, status=status.HTTP_200_OK)


# TODO: to remove after all customers on new Shopify app
class VendorStatsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Combine all statistics data view into one
    """

    def list(self, request, *args, **kwargs):
        try:
            vendor = Vendor.objects.get(shop_url=request.headers.get("Vendor"))
        except Vendor.DoesNotExist:
            logger.warning(
                f"Vendor with shop url {request.headers.get('Vendor')} does not exist"
            )
            return Response(status=status.HTTP_400_BAD_REQUEST)

        visits_count = Visit.objects.filter(vendor=vendor).count()

        products = vendor.productvendor_set.values("product")
        reco_queryset = CustomerAnalytic.objects.filter(product__in=products)
        reco_serializer = AnalyticStatSerializer(reco_queryset, many=True)
        recommendations = reco_serializer.data

        frequencies = {}
        product_frequencies = {}
        measurements = []
        total = len(recommendations)
        for reco in recommendations:
            for key, value in reco.items():
                if key == "product":
                    if value in product_frequencies:
                        product_frequencies[value] += 1
                    else:
                        product_frequencies[value] = 1
                elif key == "measurement":
                    measurements.append(value)
                else:
                    if value:
                        if key in frequencies:
                            frequencies[key] += 1
                        else:
                            frequencies[key] = 1
        product_stats = dict(
            sorted(
                product_frequencies.items(), key=operator.itemgetter(1), reverse=True
            )
        )
        frequencies["products"] = product_stats
        frequencies["total"] = total
        frequencies["visits"] = visits_count

        raw_meas_stats = {}
        for meas in measurements:
            for key, value in meas.items():
                # Have to check for None because inseam is not mandatory
                if value:
                    if key in raw_meas_stats:
                        raw_meas_stats[key].append(value)
                    else:
                        raw_meas_stats[key] = [value]

        meas_stats = {}
        for key, value in raw_meas_stats.items():
            if value:
                meas_stats[key] = {
                    "min": min(value),
                    "max": max(value),
                    "average": mean(value),
                    "median": median(value),
                    "values": value,
                }
            else:
                meas_stats[key] = {"error": "no data"}

        product_ids = products.values_list("external_id", flat=True)

        result = {
            "recommendations": frequencies,
            "measurements": meas_stats,
            "product_ids": product_ids,
        }

        return Response(data=result, status=status.HTTP_200_OK)
