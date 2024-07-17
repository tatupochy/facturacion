from django.urls import path
from .views import CustomTokenObtainPairView, CustomTokenRefreshView


urlpatterns = [
    path('seguridad/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('seguridad/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]