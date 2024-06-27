#!/usr/bin/env python3
import pytz
import random
from datetime import datetime, timedelta
from time import time
import uuid

from django.core.management.base import BaseCommand, CommandError

from customers.models import CustomerAnalytic, CustomerMeasurement
from orders.models import OrderLine
from vendors.models import Vendor, Visit


class Command(BaseCommand):
    help = "Generate demo data"

    def __create_visits(self, params, vendor):
        """Create visits objects from parameters."""
        visits = []
        for visits_num in range(params["visits"] + 1):
            visits.append(Visit(vendor=vendor, created_at=params["date"]))
        created_visits = Visit.objects.bulk_create(visits)
        print(f"Created {params['visits']} visits at date {params['date']}")

        return len(created_visits)

    def __create_order_lines(self, params, vendor):
        """Create recommendations objects from parameters."""
        order_lines = []
        for order_lines_num in range(params["order_lines"] + 1):
            if order_lines_num <= params["refunded"]:
                order_lines.append(
                    OrderLine(
                        external_id=f"demo_{uuid.uuid4()}",
                        order_external_id=f"demo_{uuid.uuid4()}",
                        amount=random.randrange(20, 200, 5),
                        created_at=params["date"],
                        refunded=True,
                        vendor=vendor,
                    )
                )
            else:
                order_lines.append(
                    OrderLine(
                        external_id=f"demo_{uuid.uuid4()}",
                        order_external_id=f"demo_{uuid.uuid4()}",
                        amount=random.randrange(20, 200, 5),
                        created_at=params["date"],
                        refunded=False,
                        vendor=vendor,
                    )
                )

        created_order_lines = OrderLine.objects.bulk_create(order_lines)
        print(f"Created {params['order_lines']} order lines at date {params['date']}")

    def __create_recommendations(self, params, vendor):
        """Create recommendations objects from parameters."""
        recommendations = list(
            CustomerAnalytic.objects.filter(product_vendor__vendor=vendor)
        )
        reco_params = params["recommendations"]
        order_lines = []
        for reco_num in range(reco_params["total"] + 1):
            reco_to_copy = random.choice(recommendations)
            reco_to_copy.pk = None
            old_cust_meas = reco_to_copy.measurement
            new_cust_meas = CustomerMeasurement.objects.create(
                customer=old_cust_meas.customer,
                bust=old_cust_meas.bust + random.randint(-3, 3),
                waist=old_cust_meas.waist + random.randint(-3, 3),
                hips=old_cust_meas.hips + random.randint(-3, 3),
                thigh=old_cust_meas.thigh + random.randint(-3, 3),
                inseam=old_cust_meas.inseam
                and old_cust_meas.inseam + random.randint(-3, 3)
                or None,
            )
            reco_to_copy.measurement = new_cust_meas
            reco_to_copy.created_at = params["date"]
            if reco_num <= reco_params["added_to_cart"]:
                reco_to_copy.added_to_cart = True
            reco_to_copy.save()
            if reco_num <= reco_params["purchased"]:
                reco_to_copy.purchased = True
                order_lines.append(
                    OrderLine(
                        external_id=f"demo_{uuid.uuid4()}",
                        order_external_id=f"demo_{uuid.uuid4()}",
                        product_vendor=reco_to_copy.product_vendor,
                        amount=random.randrange(20, 200, 5),
                        created_at=params["date"],
                        customer_analytic_id=reco_to_copy.id,
                        vendor=vendor,
                    )
                )
                reco_to_copy.save()
        created_order_lines = OrderLine.objects.bulk_create(order_lines)
        print(
            f"Created {params['recommendations']['total']} recommendations at date {params['date']}"
        )
        print(
            f"Created {params['recommendations']['purchased']} Scircula order lines at date {params['date']}"
        )

    def __get_number(self, day_num, min_cov, max_cov, total_days):
        """Get quantity from linear function."""
        return (max_cov - min_cov) / (total_days) * day_num + min_cov

    def __get_generator_params(self, start_date, end_date):
        """Generate sorted random numbers of visits and recommendations statistics."""
        generator_params = []
        total_days = int((end_date - start_date).days)
        for day_num in range(total_days + 1):
            # Number of visits by day is between 1 & 10 000
            visits = round(self.__get_number(day_num, 0, 1000, total_days))
            # Conversion rates is between 1 and 20%
            order_lines_cvr = self.__get_number(day_num, 0.01, 0.2, total_days)
            # Returns rate is between 40 and 2%
            refunded_cvr = self.__get_number(day_num, 0.4, 0.02, total_days)
            # Customer analytics conversion rate is 25%
            recommendations_cvr = self.__get_number(day_num, 0, 0.25, total_days)
            # Added to cart conversion rate is between 5 and 30%
            added_to_cart_cvr = self.__get_number(day_num, 0.05, 0.3, total_days)
            # Purchased conversion rate is between 10 and 60%
            purchased_cvr = self.__get_number(day_num, 0.1, 0.6, total_days)

            date = start_date + timedelta(days=day_num)

            order_lines = round(visits * order_lines_cvr)
            refunded = round(order_lines * refunded_cvr)

            # Should be total visits but we want to avoid having more purchased
            # recommendations than order lines
            total = round(visits * recommendations_cvr)
            added_to_cart = round(total * added_to_cart_cvr)
            purchased = round(added_to_cart * purchased_cvr)
            recommendations_params = {
                "total": total,
                "added_to_cart": added_to_cart,
                "purchased": purchased,
            }

            generator_params.append(
                {
                    "date": date,
                    "visits": visits,
                    "recommendations": recommendations_params,
                    "day_num": day_num,
                    "order_lines": order_lines,
                    "refunded": refunded,
                    "total_days": total_days,
                }
            )

        return generator_params

    def handle(self, *args, **options):
        start_time = time()
        vendor_url = "scircula.myshopify.com"
        try:
            vendor = Vendor.objects.get(shop_url=vendor_url)
        except Vendor.DoesNotExist:
            raise CommandError(f"Vendor does not exist")

        start_date = datetime.now(tz=pytz.UTC) - timedelta(days=365)
        end_date = datetime.now(tz=pytz.UTC) + timedelta(days=365)

        generator_params = self.__get_generator_params(start_date, end_date)
        for params in generator_params:
            visits_count = self.__create_visits(params, vendor)
            order_lines = self.__create_order_lines(params, vendor)
            recommendations = self.__create_recommendations(params, vendor)

        end_time = time()
        print(f"Function takes {str(timedelta(seconds=(end_time - start_time)))}")
