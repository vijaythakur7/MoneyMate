from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet

from apps.accounts.models import FinancialAccount
from apps.accounts.api.serializers import FinancialAccountSerializer
# from django.shortcuts import get_object_or_404

# class FinancialAccountListAPIView(APIView):

#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         accounts = FinancialAccount.objects.filter(
#             user=request.user
#         )

#         serializer = FinancialAccountSerializer(
#             accounts,
#             many=True,
#         )

#         return Response(
#             {
#                 "accounts": serializer.data,
#             }
#         )

#     def post(self, request):
#         serializer = FinancialAccountSerializer(
#         data=request.data
#     )

#         if serializer.is_valid():
#             account = serializer.save(
#             user=request.user
#         )

#             return Response(
#                 FinancialAccountSerializer(account).data,
#                     status=201,
#         )

#         return Response(
#         serializer.errors,
#         status=400,
#     )

# class FinancialAccountDetailAPIView(APIView):

#     permission_classes = [IsAuthenticated]

#     def get_object(self, request, account_id):
#         return get_object_or_404(
#             FinancialAccount,
#             id=account_id,
#             user=request.user,
#         )

#     def get(self, request, account_id):
#         account = self.get_object(
#             request,
#             account_id,
#         )

#         serializer = FinancialAccountSerializer(
#             account
#         )

#         return Response(
#             serializer.data,
#             status=200,
#         )

#     def put(self, request, account_id):
#         account = self.get_object(
#             request,
#             account_id,
#         )

#         serializer = FinancialAccountSerializer(
#             account,
#             data=request.data,
#         )

#         if serializer.is_valid():
#             serializer.save()

#             return Response(
#                 serializer.data,
#                 status=200,
#             )

#         return Response(
#             serializer.errors,
#             status=400,
#         )

#     def patch(self, request, account_id):
#         account = self.get_object(
#             request,
#             account_id,
#         )

#         serializer = FinancialAccountSerializer(
#             account,
#             data=request.data,
#             partial=True,
#         )

#         if serializer.is_valid():
#             serializer.save()

#             return Response(
#                 serializer.data,
#                 status=200,
#             )

#         return Response(
#             serializer.errors,
#             status=400,
#         )

#     def delete(self, request, account_id):
#         account = self.get_object(request, account_id)

#         account.delete()

#         return Response(
#             status=204,
#         )

#######################################################################

# class FinancialAccountListCreateAPIView(ListCreateAPIView):

#     permission_classes = [IsAuthenticated]

#     serializer_class = FinancialAccountSerializer

#     def get_queryset(self):
#         return FinancialAccount.objects.filter(
#             user=self.request.user
#         )

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()

#         serializer = self.get_serializer(
#             queryset,
#             many=True,
#         )

#         return Response({
#             "accounts": serializer.data,
#         })

#     def perform_create(self, serializer):
#         serializer.save(
#             user=self.request.user
#         )


# class FinancialAccountDetailAPIView(
#     RetrieveUpdateDestroyAPIView
# ):

#     permission_classes = [IsAuthenticated]

#     serializer_class = FinancialAccountSerializer

#     lookup_url_kwarg = "account_id"

#     def get_queryset(self):
#         return FinancialAccount.objects.filter(
#             user=self.request.user
#         )

########################################################################

class FinancialAccountViewSet(ModelViewSet):
    serializer_class = FinancialAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FinancialAccount.objects.filter(
            user=self.request.user
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response({
            "accounts": serializer.data,
        })

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)