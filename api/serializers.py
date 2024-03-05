from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from django.core.files.base import ContentFile
import base64

from films.models import Film

from users.models import User


class UserSerializer(UserSerializer):
    """User serializer."""
    is_subscribed = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class CreateUserSerializer(UserCreateSerializer):
    """User creation serializer."""
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)

class FilmSerializer(serializers.ModelSerializer):
    """Films serializer."""
    poster = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Film
        fields = ('id', 'name', 'kp_rate', 'year', 'genre', 'country', 'poster')