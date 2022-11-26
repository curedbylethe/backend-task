from django.test import TestCase
from .models import User
from .serializers import UserSerializer
from rest_framework import viewsets
# Create your tests here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
