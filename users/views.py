from django.urls import reverse
from rest_framework import viewsets, generics, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer, RegisterSerializer, SignUpSerializer, LoginSerializer
from .utils import Utils
from django.conf import settings
import jwt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# Create your views here.

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token

        frontend_url = '127.0.0.1:3000'
        url = 'http://' + frontend_url + reverse('signup') + '?token=' + str(token)

        email_subject = 'Complete your registration'
        email_body = 'Welcome to Sotoon!' + '\n Use the link ' \
                                            'below to complete your registration: \n' + url
        data = {'email_subject': email_subject, 'email_body': email_body, 'to_email': user.email}

        Utils.send_email(data)

        return Response(user_data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SignUp(views.APIView):
    serializer_class = SignUpSerializer

    # token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description="description",
    #                                        type=openapi.TYPE_STRING)
    # username_param_config = openapi.Parameter('username', in_=openapi.IN_QUERY, description="description",
    #                                           type=openapi.TYPE_STRING)
    # name_param_config = openapi.Parameter('name', in_=openapi.IN_QUERY, description="description",
    #                                       type=openapi.TYPE_STRING)
    # birthday_param_config = openapi.Parameter('birthday', in_=openapi.IN_QUERY, description="description",
    #                                           type=openapi.TYPE_STRING)
    # password_param_config = openapi.Parameter('password', in_=openapi.IN_QUERY, description="description",
    #                                           type=openapi.TYPE_STRING)
    # id_param_config = openapi.Parameter('id_number', in_=openapi.IN_QUERY, description="description",
    #                                     type=openapi.TYPE_STRING)
    #
    # @swagger_auto_schema(
    #     manual_parameters=[token_param_config, username_param_config, name_param_config, birthday_param_config,
    #                        password_param_config, id_param_config])
    def post(self, request):
        token = request.GET.get('token')

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data

        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            user = User.objects.get(id=payload['user_id'])

            if not user.is_verified:
                user.is_verified = True
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


# def get(self, request):
#     token = request.GET.get('token')
#
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY)
#         user = User.objects.get(id=payload['user_id'])
#         if not user.is_verified:
#             user.is_verified = True
#             user.save()
#         return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
#
#     except jwt.ExpiredSignatureError as identifier:
#         return Response({'error: Activation link has expired'}, status=status.HTTP_400_BAD_REQUEST)
#
#     except jwt.exceptions.DecodeError as identifier:
#         return Response({'error: Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
