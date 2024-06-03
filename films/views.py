import os
import requests
import json

class Movie:
    def __init__(self, data: dict):
        self.kp_id = data['kinopoiskId']
        self.name = data['nameRu'] if data['nameEn'] == '' else data['nameEn']
        self.ru_name = data['nameRu']
        self.year = data['year'].split('-')[0] if data['type'] != 'FILM' else data['year']
        self.duration = data.get('filmLength', '-')
        self.tagline = data.get('slogan', '-')
        self.description = data.get('description', 'Описание недоступно')
        self.genres = [genre['genre'] for genre in data['genres']]
        self.countries = [country['country'] for country in data['countries']]
        self.age_rating = data.get('ratingAgeLimits', '-')
        self.kp_rate = data.get('ratingKinopoisk', '-')
        self.imdb_rate = data.get('ratingImdb', '-')
        self.kp_url = data.get('webUrl', '-')
        self.premiere = data.get('premiereWorld', '-')
        self.poster = data['posterUrl']
        self.poster_preview = data['posterUrlPreview']

class SEARCH:
    def __init__(self, kp_id, name, kp_rate, year, country, genre, poster, description):
        self.kp_id = kp_id
        self.name = name
        self.kp_rate = kp_rate
        self.year = year
        self.country = country
        self.genre = genre
        self.poster = poster
        self.description = description

    @staticmethod
    def get_movie_details(token, movie_id):
        url = f'https://kinopoiskapiunofficial.tech/api/v2.2/films/{movie_id}'
        headers = {'Content-Type': 'application/json', 'X-API-KEY': token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch details for movie ID {movie_id}. Status code: {response.status_code}")
            return None

    @staticmethod
    def get_top_movies(token):
        page = 1
        results = []

        while True:
            url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/top?type=BEST_FILMS_LIST&page={page}'
            headers = {'Content-Type': 'application/json', 'X-API-KEY': token}
            response = requests.get(url, headers=headers)

            # Добавляем логирование
            print(f"URL: {url}")
            print(f"Headers: {headers}")
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            response_json = response.json()

            # Проверка на наличие ключа 'films' в ответе
            if 'films' not in response_json:
                print(f"Error: 'films' key not found in response. Response: {response_json}")
                break

            top_movies = response_json['films']

            for movie in top_movies:
                # Получение полных данных о фильме
                movie_details = SEARCH.get_movie_details(token, movie['filmId'])
                if movie_details:
                    search = SEARCH(
                        movie_details['kinopoiskId'],
                        movie_details['nameRu'],
                        movie_details.get('ratingKinopoisk', '-'),
                        movie_details['year'],
                        [country['country'] for country in movie_details['countries']],
                        [genre['genre'] for genre in movie_details['genres']],
                        movie_details['posterUrl'],
                        movie_details.get('description', 'Описание недоступно')
                    )
                    results.append(search.__dict__)

            # проверяем, есть ли следующая страница
            next_page = response_json['pagesCount']
            if page == next_page:
                break
            page += 1

        results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=3, ensure_ascii=False)

# Запуск функции для получения данных о топовых фильмах
SEARCH.get_top_movies('54023ee1-c992-4bfa-b48e-f2e7a6a2b7a4')
