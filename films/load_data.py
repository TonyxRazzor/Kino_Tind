import json
from django.conf import settings
from films.models import Film, Genre
import os
import requests

class Movie:
    def __init__(self, data: dict):
        self.kp_id = data['kp_id']
        self.name = data.get('name', []) or data.get('ru_name', [])
        self.year = data['year']
        self.kp_rate = data.get('kp_rate', 'zero')
        self.genre = data.get('genre', []) or data.get('genres', [])
        self.country = data.get('country', []) or data.get('countries', [])
        self.poster = data['poster']
        self.description = data.get('description', 'Описание недоступно')

def load_data_script():
    # Чтение данных из файла JSON
    results_path = 'films/results.json'
    with open(results_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Преобразование и сохранение словарей в базу данных
    for movie_data in data:
        movie = Movie(movie_data)

        # Проверка наличия фильма в базе данных по kp_id
        if Film.objects.filter(kp_id=movie.kp_id).exists():
            print(f"Movie {movie.name} already exists in the database. Skipping.")
            continue

        # Сохранение жанров
        genre_objects = [Genre.objects.get_or_create(name=genre)[0] for genre in movie.genre]

        # Вставка данных в таблицу Film
        print(f"Processing movie: {movie.name}")
        film = Film.objects.create(
            kp_id=movie.kp_id,
            name=movie.name,
            kp_rate=movie.kp_rate,
            year=movie.year,
            country=movie.country,
            poster=f"posters/kp/{movie.kp_id}.jpg",
            description=movie.description  # Сохраняем описание
        )
        film.genre.set(genre_objects)  # Привязываем жанры к фильму
        film.save()

        # Сохранение изображения в директорию media
        save_poster(f"posters/kp/{movie.kp_id}.jpg", movie.poster, movie.kp_id)

    print(f'Total {len(data)} films inserted successfully')

def save_poster(relative_path, poster, kp_id):
    # Аналогично вашей функции, но теперь используем kp_id в качестве части пути
    poster_path = os.path.join(settings.MEDIA_ROOT, 'posters', 'kp', f"{kp_id}.jpg")
    os.makedirs(os.path.dirname(poster_path), exist_ok=True)

    # Загрузка изображения с удаленного сервера
    response = requests.get(poster, stream=True)
    with open(poster_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=128):
            file.write(chunk)
