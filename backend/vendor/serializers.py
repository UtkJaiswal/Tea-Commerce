from rest_framework import serializers
from .models import *

class VendorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendor
        fields = '__all__'

        def create(self, validated_data):
            vendor = Vendor(email=validated_data['email'],
                    name=validated_data['name'],
                    phone=validated_data['phone'],
                    role=validated_data['role']
                    )
            vendor.set_password(validated_data['password'])
            vendor.save()

            return vendor
        
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()