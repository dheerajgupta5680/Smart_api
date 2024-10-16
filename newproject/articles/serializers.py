from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    apiKey = serializers.CharField(required=True)
    pin = serializers.CharField(write_only=True, required=True)
    clientID = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'clientID', 'apiKey', 'pin', 'token')
        
    def create(self, validated_data):
        user = CustomUser(
            username = validated_data['username'],
            email = validated_data['email'],
            clientID = validated_data['clientID'],
            apiKey = validated_data['apiKey'],
            pin = validated_data['pin'],
            token = validated_data['token']
        )
        user.set_password(validated_data['password'])  # Hashes the password
        user.save()
        return user

class OrderSerializer(serializers.Serializer):
    tradingsymbol = serializers.CharField(max_length=20)
    symboltoken = serializers.CharField(max_length=20)
    exchange = serializers.ChoiceField(choices=['NFO', 'BSE', 'NSE'])
    transactiontype = serializers.ChoiceField(choices=['BUY', 'SELL'])
    ordertype = serializers.ChoiceField(choices=['MARKET', 'LIMIT', 'SL', 'SL-M'])
    quantity = serializers.IntegerField(min_value=1)
    producttype = serializers.ChoiceField(choices=['DELIVERY', 'CARRYFORWARD', 'MARGIN', 'INTRADAY', 'BO'])
    price = serializers.FloatField(required=False)
    triggerprice = serializers.FloatField(required=False)
    squareoff = serializers.FloatField(required=False)
    stoploss = serializers.FloatField(required=False)
    trailingStopLoss = serializers.FloatField(required=False)
    disclosedquantity = serializers.IntegerField(required=False)
    duration = serializers.ChoiceField(choices=['DAY', 'IOC'])
    ordertag = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate(self, data):
        if data['ordertype'] == 'LIMIT' and data.get('price') is None:
            raise serializers.ValidationError("Price must be provided for LIMIT orders.")
        
        if data['producttype'] == 'ROBO':
            if not all([data.get('squareoff'), data.get('stoploss'), data.get('trailingStopLoss')]):
                raise serializers.ValidationError("squareoff, stoploss, and trailingStopLoss must be provided for ROBO orders.")

        return data  

class ScripTokenSerializer(serializers.Serializer):
    exchange = serializers.CharField(max_length=3, required=True)  # Example choices
    symbol = serializers.CharField(max_length=10, required=True)
    type = serializers.CharField(max_length=2, default='EQ')
    
class GetPriceSerializer(serializers.Serializer):
    exchange = serializers.CharField(max_length=3, required=True)
    symbol = serializers.CharField(max_length=10, required=True)
    symboltoken = serializers.IntegerField(required=True)

class DateRangeSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    
class AlertSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    targetprice = serializers.FloatField(required=True)
