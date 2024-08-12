from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.http import HttpResponse
from django.contrib.auth import authenticate
from .models import OrderRecord
from .serializers import *
from django.http import JsonResponse
import openpyxl
from SmartApi import SmartConnect
from logzero import logger
import pandas as pd
import pyotp
import time


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
        return Response({'message': 'Logout Successful'}, status=status.HTTP_204_NO_CONTENT)
    
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
        
        GenerateSessionView.smartApi = SmartConnect(api_key=api_key)
        data = GenerateSessionView.smartApi.generateSession(username, pwd, totp)
        
        if not data['status']:
            logger.error(data)
            return JsonResponse({'error': 'Failed to create session', 'details': data}, status=400)

        return JsonResponse({'message': 'Session created successfully', 'data': data}, status=200)
        
class ScripTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ScripTokenSerializer(data=request.data)
        
        if serializer.is_valid():
            
            exchange = serializer.validated_data['exchange']
            symbol = serializer.validated_data['symbol']
            type_suffix = serializer.validated_data['type']
            
            try:
                token_data = GenerateSessionView.smartApi.searchScrip(exchange, symbol)
                if not token_data or 'status' in token_data and not token_data['status']:
                    return JsonResponse({'error': 'Failed to retrieve token', 'details': token_data}, status=400)
                
                # Filter the data based on type_suffix if provided
                filtered_data = [
                    item for item in token_data['data']
                    if item['tradingsymbol'].endswith(type_suffix)
                ]

                if not filtered_data:
                    return JsonResponse({'error': 'No matching symbol found'}, status=404)

                # Assuming there's only one match or you return the first match
                result = filtered_data[0]
                return JsonResponse({
                    'exchange': result['exchange'],
                    'tradingsymbol': result['tradingsymbol'],
                    'symboltoken': result['symboltoken']
                }, status=200)
                
            except Exception as e:
                return JsonResponse({'error': 'Failed to retrieve token', 'details': str(e)}, status=500)
        else:
            return JsonResponse(serializer.errors, status=400)
    
class PlaceOrder(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order_details = serializer.validated_data
            try:
                order_id = GenerateSessionView.smartApi.placeOrder(order_details)
                if order_id.get('status') == True:
                    # Save order details along with response data to the database
                    OrderRecord.objects.create(
                        tradingsymbol=order_details['tradingsymbol'],
                        transactiontype=order_details['transactiontype'],
                        exchange=order_details['exchange'],
                        ordertype=order_details['ordertype'],
                        producttype=order_details['producttype'],
                        price=order_details['price'],
                        quantity=order_details['quantity'],
                        orderid=order_id['data']['orderid']
                    )
                    return Response({"message": "Order placed successfully", "order_id": order_id['data']['orderid']}, status=200)
            except Exception as e:
                return Response({"error": str(e)}, status=400)
        return Response(serializer.errors, status=400)
    
class GetPrice(APIView):
    permissions = [IsAuthenticated]
    
    def get(self, request):
        serializer = GetPriceSerializer(data=request.data)
        if serializer.is_valid():
            price_order = serializer.validated_data
            try:
                price_data = GenerateSessionView.smartApi.ltpData(price_order)
                price = price_data['data']['ltp']
                return Response({"message": "Price fetched succesfully", "price": price}, status=200)
            except Exception as e:
                return Response({"error": str(e)}, status=400)        
            
class EmergencySellAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get all holdings from the smart API
        try:
            holdings_data = GenerateSessionView.smartApi.allholding()
            holdings = holdings_data.get('data', {}).get('holdings', [])
        except Exception as e:
            logger.error(f"Failed to fetch holdings: {str(e)}")
            return JsonResponse({"error": "Failed to fetch holdings", "details": str(e)}, status=500)

        orders_sent = []
        errors = []

        for holding in holdings:
            order = {
                "variety": "NORMAL",
                "tradingsymbol": holding["tradingsymbol"],
                "symboltoken": holding["symboltoken"],
                "transactiontype": "SELL",
                "exchange": holding["exchange"],
                "ordertype": "MARKET",
                "producttype": "INTRADAY",
                "duration": "DAY",
                "price": holding["ltp"],
                "squareoff": 0,
                "stoploss": 0,
                "quantity": holding["quantity"]
            }
            try:
                # Place the sell order
                order_response = GenerateSessionView.smartApi.placeOrder(order)
                orders_sent.append(order_response)
                time.sleep(0.1)  # Throttle orders to 10 per second
            except Exception as e:
                logger.error(f"Failed to place order for {holding['tradingsymbol']}: {str(e)}")
                errors.append({holding["tradingsymbol"]: str(e)})

        return JsonResponse({"success": orders_sent, "errors": errors}, status=200)
    
class ExportExcelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get date range from request
        serializer = DateRangeSerializer(data=request.query_params)
        if serializer.is_valid():
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']
    
            orders = OrderRecord.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
            
        else:
            return Response({'error': 'No orders found for the given date range'}, status=404)

        # Create a DataFrame
        df = pd.DataFrame.from_records(orders.values(
            'tradingsymbol',
            'transactiontype',
            'exchange',
            'ordertype',
            'producttype',
            'price',
            'quantity',
            'orderid',
            'created_at'
        ))

        # Convert DataFrame to Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="filtered_orders.xlsx"'
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Orders')

        return response