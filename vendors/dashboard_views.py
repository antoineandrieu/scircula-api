import json
import logging
import operator
from collections import defaultdict
from datetime import datetime
from statistics import mean, median

from django.db.models import Avg, Count, F, Func, Sum
from django.utils.timezone import make_aware
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from customers.models import CustomerAnalytic
from customers.serializers import AnalyticStatSerializer
from orders.models import OrderLine
from products.models import ProductSize, ProductSizeVendor, ProductVendor

from .models import Vendor, Visit


class Round(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s, 2)"


class VendorViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Generic view set
    """

    def __get_vendor_from_db(self, shop_url):
        vendor = None
        try:
            vendor = Vendor.objects.get(shop_url=shop_url)
        except Vendor.DoesNotExist:
            pass

        return vendor

    def get_vendor(self, request):
        shop_url = None
        error = None
        demo = request.query_params.get("demo")
        if demo:
            shop_url = "scircula.myshopify.com"
        else:
            try:
                shop_url = request.query_params["shop_url"]
            except KeyError:
                error = "missing shop url"
        if shop_url:
            vendor = self.__get_vendor_from_db(shop_url)
            if vendor is None:
                error = f"no vendor with shop url {shop_url}"
        else:
            error = "empty shop url"
        if error:
            raise Exception(error)

        return vendor


class VendorDashboardViewSet(VendorViewSet):
    """
    Get all data for dashboard
    """

    def __get_visits(self, vendor, start_date, end_date):
        visits_queryset = Visit.objects.filter(vendor=vendor)
        if start_date:
            visits_queryset = visits_queryset.filter(created_at__gte=start_date)
        if end_date:
            visits_queryset = visits_queryset.filter(created_at__lte=end_date)

        return visits_queryset.count()

    def __get_fmf_users(self, recommendations):
        fmf_users = (
            recommendations.values(
                "measurement__bust",
                "measurement__waist",
                "measurement__hips",
                "measurement__thigh",
                "measurement__inseam",
            )
            .distinct()
            .count()
        )

        return fmf_users

    def __get_fmf_sales(self, recommendations):
        order_lines = OrderLine.objects.filter(customer_analytic__in=recommendations)
        fmf_sales = order_lines.aggregate(Sum("amount"))["amount__sum"] or 0

        return fmf_sales

    def __get_total_sales(self, order_lines):
        total_sales = order_lines.aggregate(Sum("amount"))["amount__sum"] or 0

        return total_sales

    def __get_returns(self, order_lines):
        returns = order_lines.filter(refunded=True).count()

        return returns

    def __get_store_stats(self, vendor, recommendations, start_date, end_date):
        visits = self.__get_visits(vendor, start_date, end_date)
        fmf_users = self.__get_fmf_users(recommendations)
        fmf_sales = self.__get_fmf_sales(recommendations)

        order_lines = OrderLine.objects.filter(vendor=vendor)
        if start_date:
            order_lines = order_lines.filter(created_at__gt=start_date)
        if end_date:
            order_lines = order_lines.filter(created_at__lt=end_date)
        total_sales = self.__get_total_sales(order_lines)
        returns = self.__get_returns(order_lines)

        # The returns rate is the percentage of refunded orders lines
        # on the total number of order lines
        returns_rate = (
            round((order_lines.count() and returns / order_lines.count() * 100), 1)
            or None
        )

        return {
            "visits": visits,
            "fmf_users": fmf_users,
            "fmf_sales": fmf_sales,
            "total_sales": total_sales,
            "returns": returns,
            "returns_rate": returns_rate,
        }

    def __get_recommendations_global_stats(self, recommendations):
        all_count = recommendations.count()
        added_to_cart_count = recommendations.filter(added_to_cart=True).count()
        purchased_count = recommendations.filter(purchased=True).count()

        return {
            "total": all_count,
            "added_to_cart": added_to_cart_count,
            "purchased": purchased_count,
        }

    def __get_most_recommended_products(self, recommendations):
        products_count = 10
        most_reco_products = (
            ProductVendor.objects.filter(customeranalytic__in=recommendations)
            .annotate(total=Count("id"))
            .order_by("-total")[:10]
        )
        most_recommended_products = []
        for product in most_reco_products:
            product_reco = recommendations.filter(product_vendor=product)
            added_to_cart = product_reco.filter(added_to_cart=True).count()
            purchased = product_reco.filter(purchased=True).count()
            most_recommended_products.append(
                {
                    "name": product.name,
                    "external_id": product.external_id,
                    "total": product_reco.count(),
                    "added_to_cart": added_to_cart,
                    "purchased": purchased,
                }
            )
        # Order list by total first then purchased and added to cart last
        most_recommended_products = sorted(
            most_recommended_products,
            key=lambda k: (-k["total"], -k["purchased"], -k["added_to_cart"]),
        )

        return most_recommended_products

    def __get_most_recommended_sizes(self, recommendations):
        raw_recommended_sizes = (
            ProductSize.objects.filter(customeranalytic__in=recommendations)
            .annotate(total=Count("id"))
            .order_by("-total")
            .values("total", name=F("display_size"))
        )

        # Group sizes
        # https://stackoverflow.com/questions/67907119/merge-dict-in-a-python-list
        size_frequency = defaultdict(lambda: 0)
        for raw_size in list(raw_recommended_sizes):
            size_frequency[raw_size["name"]] += raw_size["total"]
        recommended_sizes = list()
        for name, total in size_frequency.items():
            recommended_sizes.append({"name": name, "total": total})

        return recommended_sizes

    def __get_last_recommendations(self, recommendations):
        recommendations_count = 10
        last_recommendations = recommendations.values(
            "created_at",
            prod_id=F("product_vendor__external_id"),
            prod_name=F("product_vendor__name"),
            size_name=F("size__display_size"),
            bust=F("measurement__bust"),
            waist=F("measurement__waist"),
            hips=F("measurement__hips"),
            thigh=F("measurement__thigh"),
            inseam=F("measurement__inseam"),
        ).order_by("-created_at")[:recommendations_count]

        return list(last_recommendations)

    def __get_customer_stats(self, recommendations):
        recommendations_count = 10
        customer_stats = recommendations.values(
            "measurement__bust",
            "measurement__waist",
            "measurement__hips",
            "measurement__thigh",
            "measurement__inseam",
        ).aggregate(
            bust=Round(Avg("measurement__bust")),
            waist=Round(Avg("measurement__waist")),
            hips=Round(Avg("measurement__hips")),
            thigh=Round(Avg("measurement__thigh")),
            inseam=Round(Avg("measurement__inseam")),
        )

        return customer_stats

    def __get_reco_queryset(self, vendor, query_params):

        start_date = query_params.get("start_date")
        end_date = query_params.get("end_date")
        gender = query_params.get("gender")
        external_category = query_params.get("external_category")
        product = query_params.get("product")

        reco_queryset = CustomerAnalytic.objects.filter(product_vendor__vendor=vendor)

        if start_date:
            reco_queryset = reco_queryset.filter(created_at__gt=start_date)
        if end_date:
            reco_queryset = reco_queryset.filter(created_at__lt=end_date)
        if gender:
            reco_queryset = reco_queryset.filter(
                product_vendor__product__gender__iexact=gender
            )
        if external_category:
            reco_queryset = reco_queryset.filter(
                product_vendor__external_category__iexact=external_category
            )
        if product:
            reco_queryset = reco_queryset.filter(product_vendor__external_id=product)

        return reco_queryset

    def list(self, request, *args, **kwargs):
        try:
            vendor = self.get_vendor(request)
        except Exception as error:
            return Response(
                data={"error": str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        reco_queryset = self.__get_reco_queryset(vendor, self.request.query_params)
        general = self.__get_store_stats(vendor, reco_queryset, start_date, end_date)
        recommendations_stats = self.__get_recommendations_global_stats(reco_queryset)
        top_products = self.__get_most_recommended_products(reco_queryset)
        recommended_sizes = self.__get_most_recommended_sizes(reco_queryset)
        last_recommendations = self.__get_last_recommendations(reco_queryset)
        customer_stats = self.__get_customer_stats(reco_queryset)

        return Response(
            data={
                "general": general,
                "recommendations": recommendations_stats,
                "top_products": top_products,
                "sizes": recommended_sizes,
                "last_recommendations": last_recommendations,
                "customers": customer_stats,
            },
            status=status.HTTP_200_OK,
        )


class ProductVendorDashboardViewSet(VendorViewSet):
    """
    Get all products data for dashboard
    """

    def list(self, request, *args, **kwargs):
        try:
            vendor = self.get_vendor(request)
        except Exception as error:
            return Response(
                data={"error": str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        product_vendors = ProductVendor.objects.filter(vendor=vendor).values(
            "external_id", "name"
        )

        return Response(
            data=product_vendors,
            status=status.HTTP_200_OK,
        )
