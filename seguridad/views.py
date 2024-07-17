from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import AllowAny

# Create your views here.


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    # get return value of post method and add username to it
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # Add the user's username to the response data, bring the username from the login request
        response.data['name'] = request.data['username']
        return response


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]