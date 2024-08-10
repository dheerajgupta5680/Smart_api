from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from django.http import JsonResponse
from SmartApi import SmartConnect
from logzero import logger
import pyotp

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class UserLoginView(APIView):
    def post(self, request):
        user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid Credentials'}, status=400)

class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the token to log the user out
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class GenerateSessionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        api_key = user.api_key
        username = user.client_code
        pwd = user.pin
        token = user.totp_token
        
        try:
            totp = pyotp.TOTP(token).now()
        except Exception as e:
            logger.error("Invalid Token: The provided token is not valid.")
            return JsonResponse({'error': 'Invalid TOTP Token'}, status=400)
        
        smartApi = SmartConnect(api_key=api_key)
        data = smartApi.generateSession(username, pwd, totp)
        
        if not data['status']:
            logger.error(data)
            return JsonResponse({'error': 'Failed to create session', 'details': data}, status=400)

        return JsonResponse({'message': 'Session created successfully', 'data': data}, status=200)
        