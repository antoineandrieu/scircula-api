from django.db import models
from django.utils import timezone


class CustomerAnalytic(models.Model):
    product = models.ForeignKey(
        "products.Product", related_name="analytics", on_delete=models.DO_NOTHING
    )
    size = models.ForeignKey(
        "products.ProductSize", blank=True, null=True, on_delete=models.DO_NOTHING
    )
    product_size_vendor = models.ForeignKey(
        "products.ProductSizeVendor", blank=True, null=True, on_delete=models.DO_NOTHING
    )
    product_vendor = models.ForeignKey(
        "products.ProductVendor", blank=True, null=True, on_delete=models.DO_NOTHING
    )
    measurement = models.ForeignKey(
        "CustomerMeasurement", related_name="measurements", on_delete=models.DO_NOTHING
    )
    added_to_cart = models.BooleanField(blank=True, default=False)
    purchased = models.BooleanField(blank=True, default=False)
    # TODO: Replace by size foreign key when all variants has and external id
    # For now it's not the case for composed sizes
    size_added_to_cart_id = models.CharField(max_length=64, blank=True, default=False)
    added_to_cart_product_title = models.CharField(
        max_length=256, blank=True, default=False
    )
    added_to_cart_variant_title = models.CharField(
        max_length=256, blank=True, default=False
    )
    purchased_size_id = models.CharField(max_length=64, blank=True, default=False)
    purchased_product_title = models.CharField(
        max_length=256, blank=True, default=False
    )
    purchased_variant_title = models.CharField(
        max_length=256, blank=True, default=False
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "customer_analytic"


class CustomerMeasurement(models.Model):
    customer = models.ForeignKey(
        "Customer", blank=True, null=True, on_delete=models.DO_NOTHING
    )
    waist = models.IntegerField()
    bust = models.IntegerField()
    thigh = models.IntegerField()
    hips = models.IntegerField()
    inseam = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "customer_measurement"


class Customer(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.DO_NOTHING)
    vendors = models.ManyToManyField(
        "vendors.Vendor", related_name="customers", blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "customer"
