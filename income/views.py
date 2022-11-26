from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Income
from .serializers import IncomeSerializer
from rest_framework import permissions
from .permissions import IsOwnerOrReadOnly

# Create your views here.

class IncomeListAPIView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    serializer_class = IncomeSerializer
    queryset = Income.objects.all()

    def get_queryset(self):
        return Income.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class IncomeDetailAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = IncomeSerializer
    queryset = Income.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        return Income.objects.filter(owner=self.request.user)