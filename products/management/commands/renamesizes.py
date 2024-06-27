#!/usr/bin/env python3

import argparse
import difflib
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from openpyxl import Workbook, load_workbook
from products.models import Product, ProductVendor, ProductSize, ProductSizeVendor, Size
from vendors.models import Vendor


class Command(BaseCommand):
    help = "Add vendor to product from a spreadsheet"

    def add_arguments(self, parser):
        parser.add_argument("-ve", "--vendor", required=True, help="Vendor URL")

    def handle(self, *args, **options):
        vendor_url = options["vendor"]
        try:
            vendor = Vendor.objects.get(url=vendor_url)
        except Vendor.DoesNotExist:
            raise CommandError(f"Vendor with URL {options['vendor']} does not exist")

        sizes_to_rename = ProductSizeVendor.objects.filter(vendor=vendor)

        for size in sizes_to_rename:
            size_name = size.name
            if "/" in size_name and size_name != "32 / 34" and size_name != "L/XL":
                size.name = f"W{size_name[:2]} L{size_name[-2:]}"

                size.save()
