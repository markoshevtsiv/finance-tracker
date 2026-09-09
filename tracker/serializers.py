import io

from rest_framework import serializers

from tracker.models import Transaction


class TransactionSerializer(serializers.Serializer):
    category = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    date = serializers.DateField()
    description = serializers.CharField(max_length=255)

    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)

