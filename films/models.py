# films/models.py
from django.db import models
from users.models import User

class Genre(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Жанр'
        )

    def __str__(self):
        return self.name

class Film(models.Model):
    kp_id = models.IntegerField(
        db_index=True,
        verbose_name='Индекс'
    )

    name = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name='Название Фильма'
    )

    kp_rate = models.CharField(
        max_length=10,
        db_index=True,
        verbose_name='Рэйтинг'
    )

    year = models.IntegerField(
        db_index=True,
        verbose_name='Год'
    )

    genre = models.ManyToManyField(Genre)

    country = models.CharField(
        max_length=10,
        db_index=True,
        verbose_name='Страна'
    )

    poster = models.ImageField(
        upload_to='posters/kp/',
        blank=True,
        verbose_name='Постер'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        db_table = 'Film'

class FilmChoice(models.Model):
    SELECTION_CHOICES = [
        ('yes', 'Да'),
        ('no', 'Нет'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    selection = models.CharField(max_length=3, choices=SELECTION_CHOICES)
    matched = models.BooleanField(default=False)
    chosen = models.BooleanField(default=False)  # Добавлено поле chosen

    class Meta:
        unique_together = ('user', 'film', 'selection')

