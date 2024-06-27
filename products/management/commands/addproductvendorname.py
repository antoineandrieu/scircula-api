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
        parser.add_argument("-ve", "--vendor", required=True, help="Vendor URL")

    def handle(self, *args, **options):
        vendor_url = options["vendor"]
        try:
            vendor = Vendor.objects.get(shop_url=vendor_url)
        except Vendor.DoesNotExist:
            raise CommandError(f"Vendor with URL {options['vendor']} does not exist")

        product_vendors = ProductVendor.objects.filter(vendor=vendor)

        for product_vendor in product_vendors:
            if not product_vendor.name:
                product_vendor.name = product_vendor.product.name
                product_vendor.save()
