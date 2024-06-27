#!/usr/bin/env python3

import json

from django.core.management.base import BaseCommand, CommandError
from products.models import ProductVendor


class Command(BaseCommand):
    help = "Add vendor to product from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument("-i", "--input", required=True, help="JSON product file")

    def handle(self, *args, **options):
        with open(options["input"], "r+") as products_file:
            products = json.load(products_file)
            self.populate_name(products["products"])

    def populate_name(self, products):
        for product in products:
            if product.get("external_category"):
                try:
                    product_vendor = ProductVendor.objects.get(
                        external_id=product["external_id"]
                    )
                    product_vendor.external_category = product["external_category"]
                    product_vendor.save()
                except ProductVendor.DoesNotExist:
                    print(
                        f"Product vendor with {product['external_id']} does not exist"
                    )
