from django.contrib import admin

from .models import Vendor, Visit


class VisitAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_filter = ["vendor"]
    search_fields = ["vendor"]
    readonly_fields = ("created_at",)
    list_display = ("vendor", "created_at")


admin.site.register(Vendor)
admin.site.register(Visit, VisitAdmin)
