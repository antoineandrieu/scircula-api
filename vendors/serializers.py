from rest_framework import serializers

from .models import Vendor


class VendorReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ["id", "integrated_at", "currency", "scircula_plan"]


class VendorWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"
