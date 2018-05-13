from dateutil import parser
from django.http import Http404
from rest_framework import permissions, viewsets
from rest_framework.decorators import action, api_view
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
        if started >= finished:
            raise Http404

        shifts = get_shifts_to_check_for_overlaps(
            started,
            finished,
            self.request.user,
            contract.pk,
            reoccuring=reoccuring,
            exclude_shift=pk
        )
        if not shifts:
            raise Http404

        return shifts

    def get(self, request, started, finished, contract, reoccuring, pk):
        if reoccuring not in FREQUENCIES:
            raise Http404

        started = parser.parse(started, fuzzy=True)
        finished = parser.parse(finished, fuzzy=True)
        contract = Contract.objects.get(pk=contract)

        shifts = self.get_object(
            started.date(), finished.date(), contract, reoccuring, pk
        )

        good_shifts, bad_shifts = sort_overlapping_shifts(
            started, finished, self.request.user, contract, shifts
        )

        serialized_data = {
            'without_overlap': ShiftSerializer(good_shifts, many=True).data,
            'with_overlap': ShiftSerializer(bad_shifts, many=True).data,
        }

        return Response(serialized_data)
