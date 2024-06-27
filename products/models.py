import logging

from django.db import models

from vendors.models import Vendor

logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name or ""

    class Meta:
        db_table = "product_category"


class ProductCategoryAttribute(models.Model):
    category = models.ForeignKey("ProductCategory", on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=64)
    shift = models.FloatField()
    bust = models.FloatField()
    waist = models.FloatField()
    hips = models.FloatField()
    thigh = models.FloatField()

    def __str__(self):
        return "{} - {}".format(self.category, self.name) or ""

    class Meta:
        db_table = "product_category_attribute"


class Product(models.Model):
    category = models.ForeignKey(
        "ProductCategory",
        to_field="name",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    brand = models.CharField(max_length=64, blank=True, null=True)
    code = models.CharField(max_length=64, blank=True, null=True)
    gender = models.CharField(max_length=64, blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    average_stretch = models.IntegerField(blank=True, null=True)
    fabric = models.TextField(blank=True, null=True)
    fit = models.TextField(blank=True, null=True)
    file = models.FileField(blank=True, null=True)
    inseam = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.code or ""

    class Meta:
        db_table = "product"


class ProductVendor(models.Model):
    external_id = models.TextField(unique=True)
    # TODO: make it mandatory
    external_category = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_vendor"
        unique_together = ("external_id", "vendor")


class Size(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name or ""

    class Meta:
        db_table = "size"


class ProductSize(models.Model):
    product = models.ForeignKey(Product, related_name="sizes", on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.DO_NOTHING)
    display_size = models.CharField(max_length=64, blank=True, null=True)
    composed = models.BooleanField(default=False)
    inseam = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_size or ""

    class Meta:
        db_table = "product_size"


class ProductSizeVendor(models.Model):
    external_id = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE)
    # TODO: Remove this field
    vendor = models.ForeignKey(Vendor, on_delete=models.DO_NOTHING)
    # TODO: Must not be nullable
    product_vendor = models.ForeignKey(
        ProductVendor, on_delete=models.DO_NOTHING, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_size_vendor"


class ProductAttribute(models.Model):
    product_size = models.ForeignKey(
        ProductSize, related_name="attributes", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=64)
    priority = models.IntegerField(blank=True, null=True)
    tag = models.CharField(max_length=64, blank=True, null=True)
    value = models.FloatField()
    computed_value = models.FloatField(blank=True, null=True)
    grade = models.FloatField(blank=True, null=True)
    tolerance = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        product = Product.objects.get(pk=self.product_size.product_id)
        self.computed_value = self.value * (1 + product.average_stretch / 100)
        super(ProductAttribute, self).save(*args, **kwargs)

    def __str__(self):
        return "{} - {}".format(self.tag, self.product_size) or ""

    class Meta:
        db_table = "product_attribute"
