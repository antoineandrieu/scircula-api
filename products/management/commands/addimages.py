#!/usr/bin/env python3

import argparse
import difflib
import json
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from openpyxl import Workbook, load_workbook
from products.models import Product, ProductSize, ProductSizeVendor, ProductVendor, Size
from vendors.models import Vendor


class Command(BaseCommand):
    help = "Add vendor to product from a spreadsheet"

    def add_arguments(self, parser):
        parser.add_argument(
            "-i", "--input", required=True, help="Product Listing File Path"
        )
        parser.add_argument("-ve", "--vendor", required=True, help="Vendor URL")

    def handle(self, *args, **options):
        vendor_url = options["vendor"]
        try:
            vendor = Vendor.objects.get(shop_url=vendor_url)
        except Vendor.DoesNotExist:
            raise CommandError(f"Vendor with URL {options['vendor']} does not exist")

        with open(file=options["input"], mode="r") as shopify_file:
            shopify_raw_products = json.load(shopify_file)

        for product in shopify_raw_products["products"]:
            external_id = "gid://shopify/Product/" + str(product["id"])
            image = len(product["images"]) and product["images"][0]["src"]

            try:
                product_vendor = ProductVendor.objects.get(external_id=external_id)
            except ProductVendor.DoesNotExist:
                pass

            if product_vendor:
                product_vendor.image = image
                product_vendor.save()
