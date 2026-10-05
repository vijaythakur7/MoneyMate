from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import FinancialAccount
from apps.accounts.api.serializers import FinancialAccountSerializer


class FinancialAccountListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = FinancialAccount.objects.filter(
            user=request.user
        )

        serializer = FinancialAccountSerializer(
            accounts,
            many=True,
        )

        return Response(
            {
                "accounts": serializer.data,
            }
        )