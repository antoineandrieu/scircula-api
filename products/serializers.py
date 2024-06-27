from rest_framework import serializers

from .models import Product, ProductAttribute, ProductSize
from customers.serializers import CustomerAnalyticSerializer
import logging

logger = logging.getLogger(__name__)


class FileSerializer(serializers.ModelSerializer):
    # external_id = serializers.CharField(allow_null=True)

    class Meta:
        model = Product
        fields = ["file"]


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ["tag", "value"]


class ProductSizeSerializer(serializers.ModelSerializer):
    attributes = ProductAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = ProductSize
        fields = ["display_size", "attributes", "inseam"]


class ProductSerializer(serializers.ModelSerializer):
    sizes = serializers.SerializerMethodField()
    analytics = CustomerAnalyticSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ["code", "analytics", "sizes"]

    def get_sizes(self, obj):
        product_sizes = ProductSize.objects.filter(product_id=obj.id, composed=False)
        serializer = ProductSizeSerializer(instance=product_sizes, many=True)
        return serializer.data
