from django.contrib import admin

from .models import Customer, CustomerAnalytic, CustomerMeasurement


class CustomerAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    readonly_fields = (
        "created_at",
        "updated_at",
    )


class CustomerAnalyticAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_filter = (
        "product__productvendor__vendor",
        "product",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_display = ("product", "size", "get_measurement")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "product",
                    "product_vendor",
                    "product_size_vendor",
                    "size",
                    "measurement",
                    "added_to_cart",
                    "purchased",
                )
            },
        ),
        (
            "Advanced options",
            {
                "classes": ("collapse",),
                "fields": (
                    "size_added_to_cart_id",
                    "added_to_cart_product_title",
                    "purchased_size_id",
                    "purchased_product_title",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    def get_measurement(self, obj):
        meas = obj.measurement
        return f"{meas.bust} - {meas.waist} - {meas.hips} - {meas.thigh} - {meas.inseam or 'na'}"

    get_measurement.short_description = "Measurement"


class CustomerMeasurementAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_display = ("bust", "waist", "hips", "thigh", "inseam")


admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerAnalytic, CustomerAnalyticAdmin)
admin.site.register(CustomerMeasurement, CustomerMeasurementAdmin)
