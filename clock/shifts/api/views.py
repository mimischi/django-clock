from rest_framework import viewsets

from clock.shifts.api.serializers import ShiftSerializer
from clock.shifts.models import Shift


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all().order_by('-started')
    serializer_class = ShiftSerializer
