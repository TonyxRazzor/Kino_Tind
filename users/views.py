# users/views.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PreferencesForm, RegistrationForm, PartnerSelectionForm, FilmChoiceForm
from films.models import Film, Genre, FilmChoice
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

import json
from .models import User, Notification
import random


@login_required
def some_view(request):
    user = request.user
    notifications = Notification.objects.filter(user=user)
    return render(request, 'some_template.html', {'user': user, 'notifications': notifications})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:home')  # Замените 'users:home' на ваш реальный URL главной страницы
    else:
        form = RegistrationForm()

    return render(request, 'users/register.html', {'form': form})

def home(request):
    return render(request, 'users/home.html')

def partner_selection(request):
    # Предположим, что у вас есть логика для получения списка партнеров
    partners = User.objects.all()

    if request.method == 'POST':
        form = PartnerSelectionForm(request.POST)
        if form.is_valid():
            selected_partner_id = form.cleaned_data['partner']
            selected_partner = User.objects.get(id=selected_partner_id)
            # Добавьте логику, если необходимо сохранить выбранного партнера
            # Перенаправление на следующую страницу
            return redirect('users:preferences')  # Замените 'users:genre_selection' на ваш реальный URL
    else:
        form = PartnerSelectionForm()
        partner = None  # Добавьте эту строку

    return render(request, 'users/partner_selection.html', {'partners': partners, 'form': form})



def preferences(request, partner_id):
    partner = User.objects.get(id=partner_id)
    
    genre_choices = Genre.objects.values_list('name', flat=True).distinct()
    form = PreferencesForm()

    if request.method == 'POST':
        form = PreferencesForm(request.POST)
        form.update_genre_choices(genre_choices)  # Обновление вариантов выбора после создания формы
        if form.is_valid():
            selected_genres = form.cleaned_data.get('genre')
            request.session['selected_genres'] = selected_genres
            return redirect('users:film_selection')
    else:
        selected_genres = request.session.get('selected_genres', [])
        form.update_genre_choices(genre_choices)
        form.update_genre_initial(selected_genres)

    return render(request, 'users/preferences.html', {'form': form, 'partner_id': partner.id, 'genre_choices': genre_choices})


def get_genres_for_film(film):
    # Предположим, что у вас есть поле ManyToManyField с именем 'genre'
    genres = film.genre.all()
    return genres

def film_selection(request):
    selected_genres = request.session.get('selected_genres', [])
    films = get_all_films(selected_genres)

    # Фильтруем фильмы на основе выбора пользователей
    chosen_films = FilmChoice.objects.filter(user=request.user, chosen=True).values_list('film', flat=True)
    films = films.exclude(id__in=chosen_films)

    films_with_genres = [{'film': film, 'genres': get_genres_for_film(film)} for film in films]

    if request.method == 'POST':
        form = FilmChoiceForm(request.POST)
        if form.is_valid():
            film_choice = form.save(commit=False)
            film_choice.user = request.user
            film_choice.save()

            # Проверяем, есть ли совпадение с другими пользователями
            if FilmChoice.objects.filter(film=film_choice.film, matched=True).exists():
                matching_film_id = film_choice.film_id
                request.session['matching_film_ids'] = [matching_film_id]

            # Возвращаем JSON-ответ с обновленными данными о фильмах и жанрах
            return JsonResponse({'success': True, 'films_with_genres': films_with_genres, 'selected_genres': selected_genres})

    else:
        form = FilmChoiceForm()

    # Получаем film_id из запроса или из сессии
    film_id = request.GET.get('film_id') or request.session.get('film_id')

    # Добавляем film_id в контекст
    context = {'films_with_genres': films_with_genres, 'form': form, 'film_id': film_id}
    return render(request, 'users/film_selection.html', context)

def check_for_match(request):
    # Ваша логика проверки совпадения здесь
    # Если совпадение найдено, верните список идентификаторов фильмов, иначе верните None
    response = check_match(request)
    response_data = json.loads(response.content)
    if response_data.get('matched'):
        matching_film_ids = response_data.get('matching_film_ids', [])
        return matching_film_ids
    return None

@csrf_exempt
def confirm_match(request):
    if request.method == 'POST':
        user = request.user if request.user.is_authenticated else None

        film_id = request.POST.get('film_id')
        selection = request.POST.get('selection')

        film = get_object_or_404(Film, id=film_id)

        existing_choice = FilmChoice.objects.filter(user=user, film=film).first()

        if existing_choice:
            existing_choice.selection = selection
            existing_choice.save()

            naruto_film_choice = FilmChoice.objects.filter(user__username='naruto', film=film).first()

            if naruto_film_choice:
                existing_choice.matched = True
                existing_choice.save()
                naruto_film_choice.matched = True
                naruto_film_choice.save()

                matching_films = FilmChoice.objects.filter(film=film, selection=selection).exclude(user=user)
                matching_films.update(matched=True)

                matching_film_id = int(film_id)

                # После сохранения совпадения, перенаправляем на страницу совпадения
                return HttpResponseRedirect(reverse('users:confirm_match_result', args=[film_id]))

        else:
            film_choice = FilmChoice(user=user, film=film, selection=selection)
            film_choice.save()

        # Если совпадение не найдено, вернуть пустой ответ
        return JsonResponse({'success': False, 'films_with_genres': []})
    else:
        # Возвращаем HTML-страницу для не-AJAX-запросов
        return render(request, 'confirm_match_result.html')  # Замените на ваш шаблон



def confirm_match_result(request, film_id=None):
    # Добавляем проверку, если film_id не передан, используем значение из сессии

    matching_film_ids = request.session.get('matching_film_ids', [])
    print("matching_film_ids from session:", matching_film_ids)
    if matching_film_ids:
        film_id = matching_film_ids[0]

    if film_id is None:
        film_id = request.session.get('matching_film_ids', [])[0]

    film = get_object_or_404(Film, id=film_id)
    matched = False  # По умолчанию совпадения нет

    # Получаем текущего пользователя
    user = request.user

    # Проверяем, было ли совпадение с данным фильмом
    if FilmChoice.objects.filter(film=film, matched=True).exists():
        matched = True

        # Создаем уведомление для пользователя
        Notification.objects.create(user=user, message='Найдено совпадение для выбранного фильма!')
        print("messages:", user)


    print("confirm_match_result called with film_id:", film_id)
    print("matched:", matched)
    return render(request, 'users/confirm_match_result.html', {'matched': matched, 'matching_film': film})


def result(request):
    selected_film = get_selected_film_based_on_preferences({'genre': 'some_genre'})
    return render(request, 'users/result.html', {'film': selected_film})


def history(request):
    # Получение истории просмотров текущего пользователя
    viewed_films = FilmChoice.objects.filter(user=request.user)

    return render(request, 'users/history.html', {'history': viewed_films})

def get_selected_film_based_on_preferences(preferences):
    genre = preferences.get('genre')
    selected_film = Film.objects.filter(genre__name=genre).first()
    return selected_film


def get_all_films(selected_genres=None):
    # Логика получения всех фильмов из вашей базы данных
    films = Film.objects.all()

    # Если выбраны жанры, фильтруем фильмы по этим жанрам
    if selected_genres:
        films = films.filter(genre__name__in=selected_genres)

    return films

def get_user_viewed_films(user):
    # Логика получения истории просмотров пользователя из вашей базы данных
    return user.viewed_films.all()


@csrf_exempt
def check_match(request):
    print("Check match request data:", request.POST)
    print("Check match user:", request.user)
    
    user = request.user if request.user.is_authenticated else None

    # Проверяем, есть ли совпадение для текущего пользователя
    matching_film = FilmChoice.objects.filter(Q(user=user) & Q(selection='yes') & Q(matched=False)).first()

    if matching_film:
        # Если есть совпадение, помечаем его как найденное
        matching_film.matched = True
        matching_film.save()

        # Возвращаем информацию о совпадении
        response_data = {'matched': True, 'matching_film_id': matching_film.film.id}
        return JsonResponse(response_data, status=200)

    # Если совпадения нет, возвращаем JSON с информацией
    response_data = {'matched': False}
    return JsonResponse(response_data, status=200)
