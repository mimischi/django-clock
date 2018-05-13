from datetime import datetime

from dateutil import parser
from dateutil.rrule import rrule
from django.http import Http404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from clock.contracts.models import Contract
from clock.shifts.api.serializers import ShiftSerializer
from clock.shifts.models import Shift
from clock.shifts.utils import (
    FREQUENCIES,
    get_shifts_to_check_for_overlaps,
    sort_overlapping_shifts,
)


@api_view(['GET'])
def api_root(request, format=None):
    return Response(
        {
            'overlap':
            reverse('api:overlap-list', request=request, format=format)
        }
    )


class ShiftOverlapView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self, started, finished, contract, reoccuring, pk=None):
        shifts = get_shifts_to_check_for_overlaps(
            started,
            finished,
            self.request.user,
            contract,
            reoccuring=reoccuring,
            exclude_shift=pk
        )

        return shifts

    def get(self, request, started, finished, contract, reoccuring, pk):
        started = parser.parse(started, fuzzy=True)
        finished = parser.parse(finished, fuzzy=True)

        if (started >= finished) or (reoccuring not in FREQUENCIES):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            contract = Contract.objects.get(pk=contract)
        except Contract.DoesNotExist:
            contract = None

        shifts = self.get_object(
            started.date(), finished.date(), contract, reoccuring, pk
        )

        if shifts:
            good_shifts, bad_shifts = sort_overlapping_shifts(
                started, finished, self.request.user, contract, shifts
            )
            serialized_data = {
                'without_overlap': ShiftSerializer(good_shifts,
                                                   many=True).data,
                'with_overlap': ShiftSerializer(bad_shifts, many=True).data,
            }
            return Response(serialized_data)

        dates = list(
            rrule(
                freq=FREQUENCIES[reoccuring], dtstart=started, until=finished
            )
        )
        start_time = started.time()
        finish_time = finished.time()

        good_shifts = []
        for date in dates:
            started = timezone.make_aware(datetime.combine(date, start_time))
            finished = timezone.make_aware(datetime.combine(date, finish_time))
            shift = Shift(
                employee=request.user,
                contract=contract,
                started=started,
                finished=finished
            )
            good_shifts.append(shift)

        serialized_data = {
            'without_overlap': ShiftSerializer(good_shifts, many=True).data,
            'with_overlap': []
        }

        return Response(serialized_data)
