from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.forms.models import model_to_dict
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from .models import Student, Vendor


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', )


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ('user', 'budget_spent')


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        exclude = ('user')


class UserSerializerWithToken(serializers.ModelSerializer):

    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('token', 'username', 'password')

class ChangePasswordSerializer(serializers.Serializer):

    """
    Serializer for password change endpoint.
    """
    model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

