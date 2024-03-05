# Стандартные библиотеки
from django.db.models import Exists, OuterRef
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

# Сторонние библиотеки
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
#from django_filters.rest_framework import DjangoFilterBackend

# Модули проекта
from api.filters import FilmFilter
from api.paginator import CustomPaginator
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.serializers import FilmSerializer, UserSerializer
from films.models import Film
#from films.views import 
from users.models import User


class UserViewSet(UserViewSet):
    """Users' model processing viewset."""
    serializer_class = UserSerializer
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated]

class FilmViewSet(viewsets.ReadOnlyModelViewSet):
    """Films' model processing viewset."""
    serializer_class = FilmSerializer
    queryset = Film.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [FilmFilter, ]
    search_fields = ['^name', ]






    