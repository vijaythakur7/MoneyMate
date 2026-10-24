"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from apps.users.views import *
from apps.accounts.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("hello/", hello),
    path("users/<int:id>/", user_detail, name="user-detail"),
    path("search/", search, name="search"),
    path("auth/login/", login_view, name="login"),
    path("auth/logout/", logout_view, name="logout"),
    path("auth/csrf/",csrf_token_view,name="csrf-token",),
    # path("accounts/",financial_account_list,name="financial-account-list",),
    # path("accounts/<int:account_id>/",financial_account_detail,name="financial-account-detail",),
    path("api/hello/",HelloAPIView.as_view(),name="api-hello",),
    path("api/",include("apps.accounts.api.urls"),),
    path("api/auth/token/",TokenObtainPairView.as_view(),name="token_obtain_pair",),
    path("api/auth/token/refresh/",TokenRefreshView.as_view(),name="token_refresh",),
    path("api/", include("apps.users.urls")),

    # OpenAPI schema.
    path("api/schema/",SpectacularAPIView.as_view(),name="schema",
    ),

    # Interactive Swagger UI.
    path("api/docs/",SpectacularSwaggerView.as_view(url_name="schema"),name="swagger-ui",),

    # Alternative documentation UI.
    path("api/redoc/",SpectacularRedocView.as_view(url_name="schema"),name="redoc",),
    
]
