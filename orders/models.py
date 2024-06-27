from django.db import models
from django.utils import timezone


class OrderLine(models.Model):
    external_id = models.CharField(max_length=64, unique=True)
    order_external_id = models.CharField(max_length=64)
    vendor = models.ForeignKey("vendors.Vendor", on_delete=models.DO_NOTHING)
    product_vendor = models.ForeignKey(
        "products.ProductVendor", blank=True, null=True, on_delete=models.SET_NULL
    )
    product_size_vendor = models.ForeignKey(
        "products.ProductSizeVendor", blank=True, null=True, on_delete=models.SET_NULL
    )
    customer_analytic = models.ForeignKey(
        "customers.CustomerAnalytic", blank=True, null=True, on_delete=models.SET_NULL
    )
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    refunded = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "order_line"
