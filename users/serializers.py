from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from .models import User
from django.contrib import auth


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email', '')

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email is already in use'})

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class SignUpSerializer(serializers.ModelSerializer):
    # token = serializers.CharField(max_length=555)
    email = serializers.EmailField(max_length=255, min_length=3, read_only=True)
    password = serializers.CharField(max_length=50, min_length=8, write_only=True)
    username = serializers.CharField(max_length=50, min_length=6)
    name = serializers.CharField(max_length=50, min_length=4)
    id_number = serializers.CharField(min_length=8, max_length=10)
    birthday = serializers.DateField()

    def validate(self, attrs):
        username = attrs.get('username', '')
        id_number = attrs.get('id_number', '')

        if not username.isalnum():
            raise serializers.ValidationError('The username should only contain alphanumeric characters')

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': 'Username is already in use'})

        if User.objects.filter(id_number=id_number).exists():
            raise serializers.ValidationError({'id_number': 'ID number is already in use'})

        return attrs

    class Meta:
        model = User
        fields = ['username', 'name', 'id_number', 'birthday', 'password', 'email']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=50, min_length=8, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3, read_only=True)
    tokens = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['tokens', 'email', 'password', 'username']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, please try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')

        return {
            'email': user.email,
            'username': user.username,
            'token': user.tokens,
            'is_HR': user.is_HR,
            'is_Finance': user.is_Finance
        }
