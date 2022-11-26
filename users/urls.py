from django.urls import path
from .views import RegisterView, UserViewSet, SignUp, LoginAPIView
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('signup/', SignUp.as_view(), name='signup'),
]
