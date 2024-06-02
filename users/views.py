# users/views.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PreferencesForm, RegistrationForm, PartnerSelectionForm, FilmChoiceForm, ProfilePhotoForm
from films.models import Film, Genre, FilmChoice, WatchedFilm, WatchTodayFilm
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.db import IntegrityError
import logging
from django.conf import settings

import json
from .models import User, Notification, Friendship
import random

logger = logging.getLogger(__name__)


@login_required
def some_view(request):
    user = request.user
    notifications = Notification.objects.filter(user=user)
    
    # Добавим вывод уведомлений и идентификатора пользователя в логи
    print("User:", user)
    print("Notifications:", notifications)
    
    return render(request, 'some_template.html', {'user': user, 'notifications': notifications})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:home')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def home(request):
    users = User.objects.all()
    context = {
        'users': users,
        'user_id': request.user.id,  # Передача user_id в шаблон
    }
    return render(request, 'users/home.html', context)

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    friendship, created = Friendship.objects.get_or_create(from_user=request.user, to_user=to_user)
    
    if created:
        Notification.objects.create(
            user=to_user,
            title='Friend Request',
            body=f'{request.user.username} sent you a friend request.',
            is_match_notification=False
        )
        logger.debug(f'Friend request notification created for {to_user.username}')
    else:
        logger.debug(f'Friend request already exists between {request.user.username} and {to_user.username}')
    
    return redirect('users:user_profile', user_id=to_user.id)

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(Friendship, id=request_id, to_user=request.user)
    friend_request.accepted = True
    friend_request.save()

    Notification.objects.create(
        user=friend_request.from_user,
        title='Friend Request Accepted',
        body=f'{request.user.username} accepted your friend request.',
        is_match_notification=False
    )
    logger.debug(f'Friend request accepted notification created for {friend_request.from_user.username}')
    
    return redirect('users:user_profile', user_id=request.user.id)
@login_required
def remove_friend(request, friend_id):
    friend_to_remove = get_object_or_404(User, id=friend_id)
    # Удаление связи дружбы из базы данных
    Friendship.objects.filter(
        (Q(from_user=request.user, to_user=friend_to_remove) & Q(accepted=True)) |
        (Q(from_user=friend_to_remove, to_user=request.user) & Q(accepted=True))
    ).delete()

    # Создаем уведомления об удалении друга
    create_remove_friend_notification(request.user, friend_to_remove)

    # Перенаправляем пользователя на свой профиль
    return redirect('users:user_profile', user_id=request.user.id)


@login_required
def search_users(request):
    query = request.GET.get('q')
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    return render(request, 'users/search_users.html', {'users': users})

@login_required
def send_film_invitation(request, user_id):
    to_user = get_object_or_404(User, id=user_id)

    logger.debug(f'Sending film selection request from {request.user.username} to {to_user.username}')

    Notification.objects.create(
        user=to_user,
        title='Film Invitation',
        body=f'{request.user.username} invited you to select a film.',
        is_match_notification=False
    )
    logger.debug(f'Film selection request notification created for {to_user.username}')

    return redirect('users:user_profile', user_id=to_user.id)

@login_required
def user_profile(request, user_id):
    viewed_user = get_object_or_404(User, pk=user_id)
    watch_today_films = WatchTodayFilm.objects.filter(user=viewed_user)
    films_watched = WatchedFilm.objects.filter(user=viewed_user)
    
    # Проверяем, являются ли пользователи друзьями или уже отправляли запросы
    is_friend = Friendship.objects.filter(
        (Q(from_user=request.user) & Q(to_user=viewed_user) & Q(accepted=True)) |
        (Q(from_user=viewed_user) & Q(to_user=request.user) & Q(accepted=True))
    ).exists()

    # Получение списка друзей пользователя
    friends = User.objects.filter(
        Q(friendship_requests_sent__to_user=viewed_user, friendship_requests_sent__accepted=True) |
        Q(friendship_requests_received__from_user=viewed_user, friendship_requests_received__accepted=True)
    )

    sent_request = Friendship.objects.filter(from_user=request.user, to_user=viewed_user, accepted=False).exists()
    received_request = Friendship.objects.filter(from_user=viewed_user, to_user=request.user, accepted=False).first()

    default_photo_path = settings.STATIC_URL + 'photos_user/default.jpg'

    if request.method == 'POST':
        form = ProfilePhotoForm(request.POST, request.FILES)
        if form.is_valid():
            request.user.photo = form.cleaned_data['photo']
            request.user.save()
            return redirect('users:user_profile', user_id=user_id)
        else:
            if 'action' in request.POST:
                action = request.POST['action']

                if action == 'mark_watched':
                    film_id = request.POST.get('film_id')
                    watch_today_film = get_object_or_404(WatchTodayFilm, id=film_id)
                    WatchedFilm.objects.create(user=request.user, film=watch_today_film.film)
                    watch_today_film.delete()
                    return HttpResponseRedirect(request.path_info)
                
                elif action == 'send_friend_request':
                    friend_id = request.POST.get('friend_id')
                    friend = get_object_or_404(User, pk=friend_id)
                    return redirect('users:send_friend_request', user_id=friend.id)

                elif action == 'send_selection_request':
                    selected_user_id = request.POST.get('selected_user_id')
                    selected_user = get_object_or_404(User, pk=selected_user_id)
                    return redirect('users:send_film_invitation', user_id=selected_user.id)
                    
                elif action == 'remove_friend':
                    friend_to_remove = get_object_or_404(User, pk=request.POST.get('friend_id'))
                    Friendship.objects.filter(
                        (Q(from_user=request.user, to_user=friend_to_remove) & Q(accepted=True)) |
                        (Q(from_user=friend_to_remove, to_user=request.user) & Q(accepted=True))
                    ).delete()
                    
                    return redirect('users:user_profile', user_id=request.user.id)

    else:
        form = ProfilePhotoForm()

    context = {
        'viewed_user': viewed_user,
        'films_watched': films_watched,
        'watch_today_films': watch_today_films,
        'is_friend': is_friend,
        'sent_request': sent_request,
        'received_request': received_request,
        'default_photo_path': default_photo_path,
        'form': form,
        'friends': friends,
    }
    return render(request, 'users/user_profile.html', context)


def partner_selection(request):
    # Предположим, что у вас есть логика для получения списка партнеров
    partners = User.objects.all()

    if request.method == 'POST':
        form = PartnerSelectionForm(request.POST)
        if form.is_valid():
            selected_partner_id = form.cleaned_data['partner']
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
            film_choice.save()  # Убедитесь, что запись создается

            # Проверяем, есть ли совпадение с другими пользователями
            matching_film_ids = check_for_match(request)
            if matching_film_ids:
                request.session['matching_film_ids'] = matching_film_ids
                return JsonResponse({'success': True, 'redirect_url': reverse('confirm_match_result', args=[matching_film_ids[0]])})

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
    # Если совпадение найдено, верните список идентификаторов фильмов, иначе верните None
    response = check_match(request)
    response_data = json.loads(response.content)
    if response_data.get('matched'):
        matching_film_ids = response_data.get('matching_film_ids', [])
        return matching_film_ids
    return None


@csrf_exempt
def confirm_match(request):
    film_id = request.POST.get('film_id')
    selection = request.POST.get('selection')
    user = request.user

    film_choice, created = FilmChoice.objects.get_or_create(user=user, film_id=film_id, defaults={'selection': selection})
    if not created:
        film_choice.selection = selection
        film_choice.save()

    if selection == 'yes':
        # Проверка на совпадение
        match = FilmChoice.objects.filter(film_id=film_id, selection='yes').exclude(user=user).first()
        if match:
            # Обновление статуса совпадения для обоих пользователей
            film_choice.matched = True
            film_choice.save()

            match.matched = True
            match.save()

            # Создание уведомлений для обоих пользователей
            create_match_notification(user, 'Найдено совпадение для выбранного фильма!', 'Найдено совпадение для выбранного фильма!', None)
            create_match_notification(match.user, 'Найдено совпадение для выбранного фильма!', 'Найдено совпадение для выбранного фильма!', None)

            return JsonResponse({'success': True, 'film_id': film_id})

    return JsonResponse({'success': False})


from django.http import JsonResponse

@login_required
def confirm_match_result(request, film_id=None):
    print("Confirm match result function called.")
    # Проверяем существует ли переменная film_id
    if film_id is None:
        # Если нет, пытаемся получить film_id из сессии
        film_id = request.session.get('matching_film_ids', [])[0]

    # Получаем фильм по его идентификатору
    film = get_object_or_404(Film, id=film_id)

    # Устанавливаем флаг совпадения по умолчанию как False
    matched = False

    # Проверяем, существует ли совпадение с данным фильмом
    if FilmChoice.objects.filter(film=film, matched=True).exists():
        matched = True

    # Если пользователь отправил POST-запрос (нажал на кнопку), обрабатываем действие
    if request.method == 'POST':
        selection = request.POST.get('selection')
        if selection == 'yes':
            # Обработка нажатия кнопки "Буду смотреть"
            # Создаем запись о фильме для просмотра сегодня
            watch_today_film = WatchTodayFilm.objects.create(
                user=request.user,
                film=film,
                film_name=film.name,
                poster_url=film.poster.url
            )

            # Обновляем поле film после создания записи
            watch_today_film.film = film
            watch_today_film.save()

            return JsonResponse({'success': True, 'action': 'user_profile', 'user_id': request.user.id})
        elif selection == 'no':
            return JsonResponse({'success': True, 'action': 'film_selection'})

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
    logger.info("Check match request received.")
    user = request.user if request.user.is_authenticated else None

    selected_film_id = request.POST.get('film_id')
    if not selected_film_id:
        logger.error("No film_id provided in check_match request.")
        return JsonResponse({'success': False, 'message': 'Не удалось получить идентификатор фильма.'})

    # Проверяем, есть ли совпадение с другим пользователем, выбравшим "ДА" для этого же фильма
    matching_film = FilmChoice.objects.filter(Q(film_id=selected_film_id) & Q(selection='yes') & Q(matched=False)).first()

    if matching_film:
        # Создаем совпадение для текущего пользователя
        current_user_match, created = FilmChoice.objects.get_or_create(user=user, film=matching_film.film, defaults={'selection': 'yes'})
        if created:
            current_user_match.matched = True
            current_user_match.save()
        else:
            current_user_match.matched = True
            current_user_match.save(update_fields=['matched'])

        # Обновляем запись о совпадении для другого пользователя
        matching_film.matched = True
        matching_film.save(update_fields=['matched'])

        # Создаем уведомление для текущего пользователя
        create_match_notification(user, 'Найдено совпадение для выбранного фильма!', 'Найдено совпадение для выбранного фильма!', None)

        # Устанавливаем сессию для совпадения фильма
        request.session['matching_film_ids'] = [matching_film.film.id]

        response_data = {'matched': True, 'matching_film_ids': [matching_film.film.id]}
        return JsonResponse(response_data, status=200)

    logger.info("No matching film found.")
    response_data = {'matched': False}
    return JsonResponse(response_data, status=200)



@login_required
def check_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user, viewed=False).values('title', 'body', 'url')
    
    # Отладочное сообщение для проверки найденных уведомлений
    print("Found notifications:", notifications)

    # Преобразование QuerySet в список перед отправкой
    notifications_list = list(notifications)

    # Обновление статуса уведомлений на просмотренные после отправки их пользователю
    if notifications_list:
        updated_count = Notification.objects.filter(user=user, viewed=False).update(viewed=True)
        # Логирование количества обновленных уведомлений
        print(f"Updated notifications count for user {user.username}: {updated_count}")

    # Логирование найденных уведомлений
    print(f"Found notifications for user {user.username}: {list(notifications)}")

    return JsonResponse({'notifications': list(notifications)})



def create_match_notification(user, title, body, url):
    # Проверка, существует ли уже уведомление с такими параметрами
    existing_notification = Notification.objects.filter(user=user, title=title, body=body, url=url).exists()
    
    if not existing_notification:
        notification = Notification.objects.create(
            user=user,
            title=title,
            body=body,
            url=url,
            is_match_notification=True
        )
        logger.info(f"Уведомление создано для пользователя {user.id}: {notification.body}")
        return notification
    return None

def create_remove_friend_notification(sender, receiver):
    # Создаем уведомление об удалении друга для отправителя
    Notification.objects.create(
        user=sender,
        title='Friend Removed',
        body=f'You have removed {receiver.username} from your friends list.',
        is_match_notification=False
    )
    
    # Создаем уведомление об удалении друга для получателя
    Notification.objects.create(
        user=receiver,
        title='Friend Removed',
        body=f'{sender.username} has removed you from their friends list.',
        is_match_notification=False
    )

def create_film_selection_request_notification(sender, receiver):
    # Создаем уведомление о запросе на совместный выбор фильма
    Notification.objects.create(
        user=receiver,
        title='Film Selection Request',
        body=f'{sender.username} invites you to select a film together.',
        is_match_notification=False
    )

@login_required
@require_GET
def check_user_match(request):
    user = request.user  # Получить объект пользователя
    film_choice = FilmChoice.objects.filter(user=user, matched=True).first()
    
    if film_choice:
        film = film_choice.film
        # Сбросим флаг, чтобы не отправлять уведомление повторно
        film_choice.matched = False
        film_choice.save()
        return JsonResponse({'matched': True, 'film_id': film.id, 'title': film.name})
    
    return JsonResponse({'matched': False})
