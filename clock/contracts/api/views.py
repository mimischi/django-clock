from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from clock.contracts.api.serializers import ContractEndDateSerializer
from clock.contracts.models import Contract


class ContractEndDateViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated, )

    def retrieve(self, request, pk=None):
        contract = get_object_or_404(Contract, pk=pk, employee=request.user)
        serializer = ContractEndDateSerializer(contract)
        return Response(serializer.data)
