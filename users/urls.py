from django.urls import path
from .views import RegisterView, UserViewSet, EmailVerify, LoginAPIView, PasswordTokenCheckAPIView,\
    RequestPasswordResetEmail, SetNewPasswordAPIView, LogoutAPIView, SignupAPIView
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('verify-email/', EmailVerify.as_view(), name='verify-email'),
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPIView.as_view(), name='password-reset-confirm'),
    path('request-password-reset/', RequestPasswordResetEmail.as_view(), name='request-password-reset'),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name='password-reset-complete'),
]
