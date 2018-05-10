from rest_framework import serializers

from clock.shifts.models import Shift


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ('started', 'finished', 'employee', 'contract')
