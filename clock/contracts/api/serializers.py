from rest_framework import serializers

from clock.contracts.models import Contract


class ContractEndDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ('end_date', )
