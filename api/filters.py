# from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from films.models import Film


class FilmFilter(SearchFilter):
    """Products search filter model."""
    search_param = 'name'

    class Meta:
        model = Film
        fields = ('name',)