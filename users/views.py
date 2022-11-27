import os

from django.urls import reverse
from rest_framework import viewsets, generics, status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer, RegisterSerializer, EmailVerificationSerializer, LoginSerializer, \
    RequestPasswordResetEmailSerializer, SetNewPasswordSerializer, LogoutSerializer, SignupSerializer
from .utils import Utils
from django.conf import settings
import jwt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .renderers import UserRenderer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import redirect


# Create your views here.


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain
        url = 'http://' + current_site + reverse('verify-email') + '?token=' + str(token)

        email_subject = 'Complete your registration'
        email_body = 'Welcome to Sotoon!' + '\n Use the link ' \
                                            'below to complete your registration: \n' + url
        data = {'email_subject': email_subject, 'email_body': email_body, 'to_email': user.email}

        Utils.send_email(data)

        return Response(user_data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class EmailVerify(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        redirect_url = request.data.get('redirect_url', '')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()

                # return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
            if len(redirect_url) > 3:
                return redirect(redirect_url + '?token=' + str(token))
            else:
                return redirect("http://127.0.0.1:3000/auth/signup/" + '?token=' + str(token))

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error: Activation link has expired'}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.exceptions.DecodeError as identifier:
            return Response({'error: Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class SignupAPIView(generics.GenericAPIView):
    serializer_class = SignupSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request):
        # token = request.GET.get('token')
        print('token', token)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_data = serializer.data

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload['user_id'])

            if user.is_verified:
                user.username = user_data['username']
                user.name = user_data['name']
                user.birthday = user_data['birthday']
                user.id_number = user_data['id_number']
                user.set_password(user_data['password'])

                user.save()
            return Response({'account': 'Successfully verified'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error: Activation link has expired'}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.exceptions.DecodeError as identifier:
            return Response({'error: Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'error: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = RequestPasswordResetEmailSerializer

    def put(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        email = request.data['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))

            # this will invalidate the token after use
            token = PasswordResetTokenGenerator().make_token(user)

            current_site = get_current_site(request=request).domain
            relative_link = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = request.data.get('redirect_url', '')
            url = 'http://' + current_site + relative_link

            email_subject = 'Reset your password'
            email_body = 'Hi there!' + '\n Use the link ' \
                                       'below to reset your password: \n' + url + '?redirect_url=' + redirect_url
            data = {'email_subject': email_subject, 'email_body': email_body, 'to_email': user.email}

            Utils.send_email(data)

        serializer.is_valid(raise_exception=True)

        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPIView(generics.GenericAPIView):
    serializer_class = RequestPasswordResetEmailSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):

                if len(redirect_url > 3):
                    return redirect(redirect_url + '?token_valid=False')
                else:
                    return redirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')
            if len(redirect_url > 3):
                return redirect_url(
                    redirect_url + '?token_valid=True' + '&?message=Credentials_Valid&?uidb64=' + uidb64 + '&?token=' + token,
                    status=status.HTTP_302_FOUND)
            else:
                return redirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            return redirect(redirect_url + '?token_valid=False')

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Credentials valid', 'uidb64': serializer.data['uidb64'],
                         'token': serializer.data['token']}, status=status.HTTP_200_OK)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': 'Successfully logged out'}, status=status.HTTP_204_NO_CONTENT)
