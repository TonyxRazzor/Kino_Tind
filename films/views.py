# Kino_Tind(0.1)\Kino_Viewer\films\views.py
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
    def load_results():
        results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.json')
        if os.path.exists(results_path):
            with open(results_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []

    @staticmethod
    def save_results(results):
        results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=3, ensure_ascii=False)

    @staticmethod
    def get_popular_movies(token, limit=50):
        try:
            processed_movies = SEARCH.load_results()
            page = 1
            results = []

            while len(results) < limit:
                url = f'https://kinopoiskapiunofficial.tech/api/v2.2/films/collections?type=TOP_POPULAR_MOVIES&page={page}'
                headers = {'Content-Type': 'application/json', 'X-API-KEY': token}
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    return f"Failed to fetch popular movies. Status code: {response.status_code}"

                response_json = response.json()

                if 'items' not in response_json:
                    return f"Error: 'items' key not found in response. Response: {response_json}"

                movies = response_json['items']

                for movie in movies:
                    movie_id = movie.get('filmId') or movie.get('kinopoiskId')
                    if not movie_id:
                        print("Warning: Neither 'filmId' nor 'kinopoiskId' found in movie:", movie)
                        continue

                    if movie_id in [m['kp_id'] for m in processed_movies]:
                        print(f"Movie {movie_id} already processed. Skipping...")
                        continue

                    movie_details = SEARCH.get_movie_details(token, movie_id)
                    if movie_details:
                        movie_obj = Movie(movie_details)
                        results.append(movie_obj.__dict__)

                    if len(results) >= limit:
                        break

                total_pages = response_json.get('totalPages')
                if page == total_pages:
                    break
                page += 1

            SEARCH.save_results(processed_movies + results)
            return "success"
        
        except Exception as e:
            return str(e)

    @staticmethod
    def get_top_movies(token, limit=50):
        try:
            processed_movies = SEARCH.load_results()
            page = 1
            results = []

            while len(results) < limit:
                url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/top?type=BEST_FILMS_LIST&page={page}'
                headers = {'Content-Type': 'application/json', 'X-API-KEY': token}
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    return f"Failed to fetch top movies. Status code: {response.status_code}"

                response_json = response.json()

                if 'films' not in response_json:
                    return f"Error: 'films' key not found in response. Response: {response_json}"

                top_movies = response_json['films']

                for movie in top_movies:
                    movie_id = movie['filmId']

                    if movie_id in [m['kp_id'] for m in processed_movies]:
                        print(f"Movie {movie_id} already processed. Skipping...")
                        continue

                    movie_details = SEARCH.get_movie_details(token, movie_id)
                    if movie_details:
                        movie_obj = Movie(movie_details)
                        results.append(movie_obj.__dict__)

                    if len(results) >= limit:
                        break

                next_page = response_json['pagesCount']
                if page == next_page:
                    break
                page += 1

            SEARCH.save_results(processed_movies + results)
            return "success"
        
        except Exception as e:
            return str(e)

# Запуск функции для получения данных о топовых фильмах
SEARCH.get_top_movies('54023ee1-c992-4bfa-b48e-f2e7a6a2b7a4')

SEARCH.get_popular_movies('54023ee1-c992-4bfa-b48e-f2e7a6a2b7a4')
