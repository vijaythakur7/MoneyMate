from django.urls import path

from apps.users.views import UserRegistrationAPIView

urlpatterns = [
    path(
        "auth/register/",
        UserRegistrationAPIView.as_view(),
        name="api-user-register",
    ),
]