
from django.urls import path, include
from .views import *

urlpatterns = [ 
               
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('session/', GenerateSessionView.as_view(), name='GenerateSession'),
    path('symboltoken/', ScripTokenView.as_view(), name='symbol-token'),
    path('place-order/', PlaceOrder.as_view(), name='place-order'),
    path('get-price/', GetPrice.as_view(), name='get-price'),
    path('kill-switch/', EmergencySellAPIView.as_view(), name='kill-switch'),
    path('export_excel/', ExportExcelAPIView.as_view(), name='export_excel'),
]
