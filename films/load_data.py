import json
from django.conf import settings
from films.models import Film, Genre
import os
import requests

class Movie:
    def __init__(self, data: dict):
        self.kp_id = data['kp_id']
        self.name = data['name']
        self.year = data['year']
        self.kp_rate = data['kp_rate']
        self.genre = data['genre']
        self.country = data['country']
        self.poster = data['poster']

def load_data_script():
    # Чтение данных из файла JSON
    results_path = 'films/results.json'
    with open(results_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Преобразование и сохранение словарей в базу данных
    for movie_data in data:
        movie = Movie(movie_data)

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
            poster=f"posters/kp/{movie.kp_id}.jpg"
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