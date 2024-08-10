from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    totp = serializers.CharField(write_only=True, required=True)
    pin = serializers.CharField(write_only=True, required=True)
    clientID = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'clientID', 'totp', 'pin')
        
    def create(self, validated_data):
        user = CustomUser(
            username = validated_data['username'],
            email = validated_data['email'],
            clientID = validated_data['clientID'],
            totp = validated_data['totp'],
            pin = validated_data['pin']
        )
        user.set_password(validated_data['password'])  # Hashes the password
        user.save()
        return user
    