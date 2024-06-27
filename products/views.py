import json
import logging

from dataset_parser import parser
from django.db import IntegrityError
from rest_framework import mixins, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from vendors.models import Vendor

from .models import (
    Product,
    ProductAttribute,
    ProductCategory,
    ProductSize,
    ProductSizeVendor,
    ProductVendor,
    Size,
)
from .serializers import FileSerializer, ProductSerializer

logger = logging.getLogger(__name__)


class ProductViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    parser_class = (MultiPartParser,)
    serializer_class = ProductSerializer

    def get_queryset(self):
        vendor = None
        try:
            vendor = Vendor.objects.get(shop_url=self.request.headers.get("Vendor"))
        except Vendor.DoesNotExist:
            logger.error("No vendor")

        queryset = []
        external_id = self.request.query_params.get("external_id", None)
        if vendor:
            if external_id:
                try:
                    product_vendor = ProductVendor.objects.get(
                        external_id=external_id, vendor=vendor
                    )
                    queryset = [product_vendor.product]
                except:
                    logger.error("No product Vendor")
            else:
                queryset = Product.objects.filter(productvendor__vendor=vendor)

        return queryset

    def save_attributes(
        self, product, attributes, priorities, vendor, inseam_size=False
    ):
        for size, attrs in attributes.items():
            composed = False
            if not bool(attrs):
                composed = True

            # Create size & product size if doesn't exist
            try:
                db_size = Size.objects.get(name=size)
            except Size.DoesNotExist:
                db_size = Size(name=size)
                db_size.save()

            try:
                product_size = ProductSize.objects.get(
                    product=product, size=db_size, inseam=inseam_size, composed=composed
                )
            except ProductSize.DoesNotExist:
                product_size = ProductSize(
                    size=db_size,
                    product=product,
                    display_size=size,
                    inseam=inseam_size,
                    composed=composed,
                )
                product_size.save()

            for tag, value in attrs.items():
                if tag == "chest":
                    tag = "waist"
                elif tag == "neck":
                    tag = "bust"
                elif tag == "back":
                    tag = "hips"
                elif tag == "height":
                    tag = "thigh"

                try:
                    attribute = ProductAttribute.objects.get(
                        product_size=product_size.id, tag=tag
                    )
                    attribute.value = value
                except ProductAttribute.DoesNotExist:
                    attribute = ProductAttribute(
                        tag=tag, value=value, product_size=product_size
                    )
                priority = 0
                if priorities and priorities.get(tag) and priorities[tag] == 1:
                    priority = 1
                attribute.priority = priority
                attribute.save()

    def create(self, request):
        try:
            vendor = Vendor.objects.get(shop_url=request.headers["Vendor"])
        except Vendor.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        file_serializer = FileSerializer(data=request.data)

        if file_serializer.is_valid():
            product_data = parser.parse_goodsociety(request.data.get("file"), True)
            print(product_data)

            code = product_data.get("code")
            if not code:
                return Response(
                    {"error": "missing style code"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                product = Product.objects.get(code=code)
                status_code = status.HTTP_200_OK
            except Product.DoesNotExist:
                product = file_serializer.save()
                status_code = status.HTTP_201_CREATED
                product.save()

            priorities = None
            try:
                priorities = product_data.pop("priorities")
            except KeyError:
                logger.error("No priorities has been provided by this parser")

            category_exists = ProductCategory.objects.filter(
                name=product_data["category"]
            ).exists()
            if not category_exists:
                return Response(
                    {"errors": f"category {product_data['category']} does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            product_attributes = product_data.pop("attributes")
            inseam_attributes = None
            try:
                inseam_attributes = product_data.pop("inseam_attributes")
            except KeyError:
                pass

            Product.objects.filter(pk=product.id).update(**product_data)

            self.save_attributes(product, product_attributes, priorities, vendor)
            if inseam_attributes:
                self.save_attributes(
                    product,
                    inseam_attributes,
                    priorities,
                    vendor,
                    inseam_size=True,
                )
                if not product.inseam:
                    Product.objects.filter(pk=product.id).update(inseam=True)

            return Response(status=status_code)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductVendorViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer

    def get_product(self, product_code):
        product = None
        try:
            product_code = str(product_code)
        except ValueError:
            pass
        try:
            return Product.objects.get(code=product_code)
        except Product.DoesNotExist:
            raise

    def create_or_update_product_vendor(self, product, vendor, product_vendor_data):
        external_id = product_vendor_data.get("external_id")
        name = product_vendor_data.get("name")
        description = product_vendor_data.get("description")
        external_category = product_vendor_data.get("external_category")

        try:
            product_vendor = ProductVendor.objects.create(
                product=product,
                external_id=external_id,
                name=name,
                description=description,
                vendor=vendor,
                external_category=external_category,
            )
        except IntegrityError:
            product_vendor = ProductVendor.objects.get(
                external_id=external_id,
            )
            if name:
                product_vendor.name = name
            if description:
                product_vendor.description = description
            product_vendor.save()

        return product_vendor

    def decompose_sizes(self, full_sizes):
        decomposed_sizes = []
        for size in full_sizes:
            name = size["name"]
            if "/" in size["name"]:
                waist_size = {"name": name[:2], "composed": False}
                length_size = {"name": name[-2:], "inseam": True}
                if waist_size not in decomposed_sizes:
                    decomposed_sizes.append(waist_size)
                if length_size not in decomposed_sizes:
                    decomposed_sizes.append(length_size)

        return full_sizes + decomposed_sizes

    def create_or_update_product_vendor_sizes(self, product_vendor, sizes_data):
        sizes = self.decompose_sizes(sizes_data)

        errors = []
        for size in sizes:
            try:
                db_size = Size.objects.get(name=size["name"])
            except Size.DoesNotExist:
                db_size = Size(name=size["name"])
                db_size.save()
            try:
                product_size = ProductSize.objects.get(
                    product=product_vendor.product,
                    size=db_size,
                    inseam=size.get("inseam", False),
                )
                try:
                    ProductSizeVendor.objects.create(
                        product_size=product_size,
                        product_vendor=product_vendor,
                        vendor=product_vendor.vendor,
                        external_id=size.get("external_id"),
                        name=size["name"],
                    )
                except IntegrityError:
                    product_size_vendor = ProductSizeVendor.objects.get(
                        external_id=size["external_id"],
                    )
                    if product_size_vendor.name != size["name"]:
                        product_size_vendor.name = size["name"]
                        product_size_vendor.save()
            except ProductSize.DoesNotExist:
                errors.append((product_vendor.product.code, size["name"]))

        return errors

    def create(self, request):
        try:
            vendor = Vendor.objects.get(shop_url=request.headers["Vendor"])
        except Vendor.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        file_serializer = FileSerializer(data=request.data)

        if file_serializer.is_valid():
            product_vendor_data_list = parser.parse_productvendors(
                request.data.get("file"), False
            )

            errors = {}
            for product_vendor_data in product_vendor_data_list:
                product_code = product_vendor_data.get("product_code")

                if product_code and product_vendor_data.get("notes") == "to load":
                    try:
                        product = self.get_product(product_code)

                        product_vendor = self.create_or_update_product_vendor(
                            product, vendor, product_vendor_data
                        )

                        product_size_errors = (
                            self.create_or_update_product_vendor_sizes(
                                product_vendor, product_vendor_data["sizes"]
                            )
                        )
                        if product_size_errors:
                            if errors.get("missing_size"):
                                errors["missing_size"].update(set(product_size_errors))
                            else:
                                errors = {"missing_size": set(product_size_errors)}
                    except Product.DoesNotExist:
                        if errors.get("missing_products"):
                            errors["missing_products"].add(product_code)
                        else:
                            errors["missing_products"] = set([product_code])

        return Response(
            data={"errors": errors},
            status=status.HTTP_201_CREATED,
        )
