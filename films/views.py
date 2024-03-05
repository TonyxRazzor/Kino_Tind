import os
import requests
import json
#from bs4 import BeautifulSoup
class Movie:
    def __init__(self, data: dict):
        self.kp_id = data['filmId']
        self.name = data['nameRu'] if data['nameEn'] == '' else data['nameEn']
        self.ru_name = data['nameRu']
        self.year = data['year'].split('-')[0] if data['type'] != 'FILM' else data['year']
        self.duration = data['filmLength']
        self.tagline = data['slogan'] if data['slogan'] is not None else '-'
        self.description = data['shortDescription']
        self.genres = [genre['genre'] for genre in data['genres']]
        self.countries = [country['country'] for country in data['countries']]
        self.age_rating = data['ratingAgeLimits']
        self.kp_rate = data['kp_rate']
        self.imdb_rate = data['imdb_rate']
        self.kp_url = data['webUrl']
        self.premiere = data['premiereWorld']
        self.poster = data['posterUrl']
        self.poster_preview = data['posterUrlPreview']


class SEARCH:
    def __init__(self, kp_id, name, kp_rate, year, country, genre, poster):
        self.kp_id = kp_id
        self.name = name
        self.kp_rate = kp_rate
        self.year = year
        self.country = country
        self.genre = genre
        self.poster = poster
        #self.description = description

    def get_top_movies(token):
        page = 1
        results = []

        while True:
            url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/top?type=BEST_FILMS_LIST&page={page}'
            headers = {'Content-Type': 'application/json', 'X-API-KEY': token}
            response = requests.get(url, headers=headers)
            top_movies = response.json()['films']

            for movie in top_movies:
                search = SEARCH(
                    movie['filmId'],
                    movie['nameRu'],
                    movie['rating'],
                    movie['year'],
                    [country['country'] for country in movie['countries']],
                    [genre['genre'] for genre in movie['genres']],
                    movie['posterUrl']
                )
                results.append(search.__dict__)

            # проверяем, есть ли следующая страница
            next_page = response.json()['pagesCount']
            if page == next_page:
                break
            page += 1
            results.append(search.__dict__)
        with open(os.path.dirname(os.path.abspath(__file__)) + '/results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=3, ensure_ascii=False)

SEARCH.get_top_movies('54023ee1-c992-4bfa-b48e-f2e7a6a2b7a4')