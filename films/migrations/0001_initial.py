# Generated by Django 4.2.6 on 2024-01-17 07:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Жанр')),
            ],
        ),
        migrations.CreateModel(
            name='Film',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kp_id', models.IntegerField(db_index=True, verbose_name='Индекс')),
                ('name', models.CharField(db_index=True, max_length=50, verbose_name='Название Фильма')),
                ('kp_rate', models.CharField(db_index=True, max_length=10, verbose_name='Рэйтинг')),
                ('year', models.IntegerField(db_index=True, verbose_name='Год')),
                ('country', models.CharField(db_index=True, max_length=10, verbose_name='Страна')),
                ('poster', models.ImageField(blank=True, upload_to='posters/kp/', verbose_name='Постер')),
                ('genre', models.ManyToManyField(to='films.genre')),
            ],
            options={
                'verbose_name': 'Фильм',
                'verbose_name_plural': 'Фильмы',
                'db_table': 'Film',
            },
        ),
        migrations.CreateModel(
            name='FilmChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selection', models.CharField(choices=[('yes', 'Да'), ('no', 'Нет')], max_length=3)),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='films.film')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'film', 'selection')},
            },
        ),
    ]
