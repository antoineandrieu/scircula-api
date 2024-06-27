from rest_framework import serializers

from .models import CustomerAnalytic, CustomerMeasurement


class AnalyticInputSerializer(serializers.Serializer):
    measurement = serializers.PrimaryKeyRelatedField(
        queryset=CustomerAnalytic.objects.all()
    )
    product = serializers.StringRelatedField()

    class Meta:
        model = CustomerAnalytic
        fields = ["measurement", "product"]


class AnalyticOutputSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomerAnalytic
        fields = ["customer", "measurement", "size", "product"]


class AnalyticUpdateSerializer(serializers.ModelSerializer):
    size = serializers.CharField()

    class Meta:
        model = CustomerAnalytic
        fields = [
            "added_to_cart",
            "purchased",
            "size",
            "size_added_to_cart_id",
            "added_to_cart_product_title",
            "purchased_size_id",
            "purchased_product_title",
        ]


class CustomerMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerMeasurement
        fields = ["bust", "waist", "hips", "thigh", "inseam"]


class AnalyticStatSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    measurement = CustomerMeasurementSerializer()

    class Meta:
        model = CustomerAnalytic
        fields = ["product", "added_to_cart", "purchased", "measurement"]


class CustomerAnalyticSerializer(serializers.ModelSerializer):
    measurement = CustomerMeasurementSerializer()
    size = serializers.StringRelatedField()

    class Meta:
        model = CustomerAnalytic
        fields = ["measurement", "size", "added_to_cart", "purchased"]


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerMeasurement
        fields = ["bust", "hips", "thigh", "waist"]
