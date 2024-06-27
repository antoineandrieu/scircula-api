from django.contrib import admin

from .models import (
    Product,
    ProductCategory,
    ProductCategoryAttribute,
    ProductAttribute,
    ProductSize,
    ProductSizeVendor,
    ProductVendor,
    Size,
)


class ProductAdmin(admin.ModelAdmin):
    date_hierarchy = "updated_at"
    list_filter = ("productvendor__vendor", "brand", "category")
    search_fields = ("code", "name", "brand")
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_display = ("code", "name", "brand")


class ProductAttributeAdmin(admin.ModelAdmin):
    date_hierarchy = "updated_at"
    list_filter = (
        "product_size__product__brand",
        "product_size__product__category",
    )
    search_fields = ("tag",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_display = ("get_product", "product_size", "tag", "priority")
    fieldsets = (
        (
            None,
            {"fields": ("product_size", "tag", "priority", "value", "computed_value")},
        ),
        (
            "Advanced options",
            {
                "classes": ("collapse",),
                "fields": (
                    "name",
                    "grade",
                    "tolerance",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    def get_product(self, obj):
        return obj.product_size.product

    get_product.short_description = "Product"


class ProductSizeAdmin(admin.ModelAdmin):
    date_hierarchy = "updated_at"
    search_fields = ("product__code", "product__name", "size__name", "product__id")
    list_filter = (
        "product__brand",
        "product__category",
        "product",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_display = ("product", "size")
    fieldsets = (
        (None, {"fields": ("product", "size")}),
        (
            "Advanced options",
            {
                "classes": ("collapse",),
                "fields": (
                    "display_size",
                    "composed",
                    "inseam",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


class ProductSizeVendorAdmin(admin.ModelAdmin):
    date_hierarchy = "updated_at"
    search_fields = (
        "external_id",
        "product_size__product__name",
        "product_size__size__name",
    )
    list_filter = (
        # "product_vendor__vendor",
        "vendor",
        "product_size__product__brand",
        "product_size__product__category",
        "product_size__product",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_display = (
        "product_size",
        "get_product",
        # "product_vendor__vendor",
        "external_id",
    )

    def get_product(self, obj):
        return obj.product_size.product

    get_product.short_description = "Product"


class ProductVendorAdmin(admin.ModelAdmin):
    date_hierarchy = "updated_at"
    search_fields = ("external_id", "product__name", "product__brand")
    list_filter = ("vendor", "product__brand")
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_display = ("product", "vendor")


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAttribute, ProductAttributeAdmin)
admin.site.register(ProductCategory)
admin.site.register(ProductCategoryAttribute)
admin.site.register(ProductSize, ProductSizeAdmin)
admin.site.register(ProductSizeVendor, ProductSizeVendorAdmin)
admin.site.register(ProductVendor, ProductVendorAdmin)
admin.site.register(Size)
