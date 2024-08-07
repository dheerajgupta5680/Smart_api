
from django.urls import path, include
from .views import *

urlpatterns = [
    path('auth/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('logout/', LogoutAPIView.as_view(), name='logout')
]
