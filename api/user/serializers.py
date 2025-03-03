from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User 

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the default User model"""
    class Meta:
        model = get_user_model()
        fields = ['password', 'username', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )
    username = serializers.CharField()

    def validate(self, attrs):
        """Validate and authenticate the user"""
        password = attrs.get('password')
        email = attrs.get('email')
        username = attrs.get('username')

        user = authenticate(
            email=email,
            password=password,
            username=username,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs