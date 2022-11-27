from django.urls import reverse
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import User
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
import jwt
from django.conf import settings
from rest_framework.response import Response



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


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, min_length=8, write_only=True)
    username = serializers.CharField(max_length=50, min_length=6)
    name = serializers.CharField(max_length=50, min_length=4)
    id_number = serializers.CharField(min_length=8, max_length=10)
    birthday = serializers.DateField()
    token = serializers.CharField(max_length=555)

    # redirect_url = serializers.CharField(max_length=500, min_length=3, required=False)

    def validate(self, attrs):
        token = attrs.get('token', '')
        name = attrs.get('name', '')
        username = attrs.get('username', '')
        id_number = attrs.get('id_number', '')
        password = attrs.get('password', '')
        birthday = attrs.get('birthday', '')

        if not username.isalnum():
            raise serializers.ValidationError('The username should only contain alphanumeric characters')

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': 'Username is already in use'})

        if User.objects.filter(id_number=id_number).exists():
            raise serializers.ValidationError({'id_number': 'ID number is already in use'})

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload['user_id'])

            if user.is_verified:
                user.username = username
                user.name = name
                user.birthday = birthday
                user.id_number = id_number
                user.set_password(password)

                user.save()

                return user
            return super().validate(attrs)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error: Activation link has expired'}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.exceptions.DecodeError as identifier:
            return Response({'error: Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'error: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


    class Meta:
        model = User
        fields = ['username', 'name', 'id_number', 'birthday', 'password', 'token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=50, min_length=8, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3, read_only=True)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])
        return {
            'access': user.tokens()['access'],
            'refresh': user.tokens()['refresh']
        }

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


class RequestPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)
    redirect_url = serializers.CharField(max_length=500, min_length=3, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, max_length=50, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return user
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)

        return super().validate(attrs)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Token is expired or invalid'
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')
