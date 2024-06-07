from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.db.models import Q
import json
import logging

from films.models import WatchedFilm, WatchTodayFilm, Film, FilmChoice
from users.models import User, Friendship, Notification
from users.forms import RegistrationForm, ProfilePhotoForm, PartnerSelectionForm, PreferencesForm, FilmChoiceForm

logger = logging.getLogger(__name__)

# Регистрация пользователя
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

# Главная страница пользователей
def home(request):
    users = User.objects.all()
    context = {
        'users': users,
        'user_id': request.user.id,
    }
    return render(request, 'users/home.html', context)

# Отправка запроса на добавление в друзья
@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    friendship, created = Friendship.objects.get_or_create(from_user=request.user, to_user=to_user)
    
    if created:
        create_friend_request_notification(request.user, to_user)
    else:
        logger.debug(f'Friend request already exists between {request.user.username} and {to_user.username}')
    
    return redirect('users:user_profile', user_id=to_user.id)

# Принятие запроса на добавление в друзья
@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(Friendship, id=request_id, to_user=request.user)
    friend_request.accepted = True
    friend_request.save()
    create_friend_accept_notification(friend_request.from_user, request.user)
    return redirect('users:user_profile', user_id=request.user.id)

# Удаление друга
@login_required
def remove_friend(request, friend_id):
    friend_to_remove = get_object_or_404(User, id=friend_id)
    Friendship.objects.filter(
        (Q(from_user=request.user, to_user=friend_to_remove) & Q(accepted=True)) |
        (Q(from_user=friend_to_remove, to_user=request.user) & Q(accepted=True))
    ).delete()
    create_remove_friend_notification(request.user, friend_to_remove)
    return redirect('users:user_profile', user_id=request.user.id)

# Поиск пользователей
@login_required
def search_users(request):
    query = request.GET.get('q')
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    return render(request, 'users/search_users.html', {'users': users})

# Отправка приглашения на выбор фильма
@login_required
def send_film_invitation(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    create_film_selection_request_notification(request.user, to_user)
    return redirect('users:preferences', partner_id=user_id)

# Профиль пользователя
@login_required
def user_profile(request, user_id):
    viewed_user = get_object_or_404(User, pk=user_id)
    watch_today_films = WatchTodayFilm.objects.filter(user=viewed_user)
    films_watched = WatchedFilm.objects.filter(user=viewed_user)
    
    is_friend = Friendship.objects.filter(
        (Q(from_user=request.user) & Q(to_user=viewed_user) & Q(accepted=True)) |
        (Q(from_user=viewed_user) & Q(to_user=request.user) & Q(accepted=True))
    ).exists()

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
                    film = get_object_or_404(Film, id=film_id)
                    WatchedFilm.objects.get_or_create(user=request.user, film=film)
                    return redirect('users:user_profile', user_id=user_id)

                if action == 'send_friend_request':
                    return send_friend_request(request, user_id)

                if action == 'accept_friend_request':
                    return accept_friend_request(request, received_request.id)

                if action == 'remove_friend':
                    return remove_friend(request, user_id)

                if action == 'send_film_invitation':
                    return send_film_invitation(request, user_id)

    else:
        form = ProfilePhotoForm()

    context = {
        'viewed_user': viewed_user,
        'form': form,
        'friends': friends,
        'sent_request': sent_request,
        'received_request': received_request,
        'watch_today_films': watch_today_films,
        'films_watched': films_watched,
        'is_friend': is_friend,
        'default_photo_path': default_photo_path,
    }

    return render(request, 'users/user_profile.html', context)

# Выбор партнера
@login_required
def partner_selection(request, partner_id):
    partner = get_object_or_404(User, id=partner_id)

    if request.method == 'POST':
        form = PartnerSelectionForm(request.POST)
        if form.is_valid():
            # Сохранение выбранного партнера
            pass
    else:
        form = PartnerSelectionForm()

    return render(request, 'users/partner_selection.html', {'form': form, 'partner': partner})


# Управление предпочтениями пользователя для выбора фильма
@login_required
def preferences(request, partner_id):
    partner = get_object_or_404(User, id=partner_id)
    preferences_form = PreferencesForm(request.POST or None)

    if preferences_form.is_valid():
        # Сохранение предпочтений пользователя
        preferences = preferences_form.save(commit=False)
        preferences.user = request.user
        preferences.save()
        return redirect('users:film_selection', partner_id=partner_id)

    return render(request, 'users/preferences.html', {'form': preferences_form, 'partner': partner})

# Выбор фильма
@login_required
def film_selection(request, partner_id):
    partner = get_object_or_404(User, id=partner_id)
    films = Film.objects.all()
    film_choice_form = FilmChoiceForm(request.POST or None)

    if film_choice_form.is_valid():
        film_choice = film_choice_form.save(commit=False)
        film_choice.user = request.user
        film_choice.partner = partner
        film_choice.save()
        check_for_match(request.user, partner, film_choice.film)
        return redirect('users:confirm_match_result', film_id=film_choice.film.id, partner_id=partner.id)

    return render(request, 'users/film_selection.html', {'form': film_choice_form, 'films': films, 'partner': partner})

# Подробная информация о фильме
@login_required
def film_detail(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    return render(request, 'users/film_detail.html', {'film': film})

# Подтверждение совпадения выбора фильма
@login_required
def confirm_match(request, film_id, partner_id):
    film = get_object_or_404(Film, id=film_id)
    partner = get_object_or_404(User, id=partner_id)
    create_match_notification(request.user, partner, film)
    return redirect('users:confirm_match_result', film_id=film.id, partner_id=partner.id)

# Результат подтверждения совпадения
@login_required
def confirm_match_result(request, film_id, partner_id):
    film = get_object_or_404(Film, id=film_id)
    partner = get_object_or_404(User, id=partner_id)
    return render(request, 'users/confirm_match_result.html', {'film': film, 'partner': partner})

# История просмотренных фильмов
@login_required
def history(request):
    films_watched = WatchedFilm.objects.filter(user=request.user)
    return render(request, 'users/history.html', {'films_watched': films_watched})

# Проверка уведомлений
def check_notifications(request):
    if not request.user.is_authenticated:
        logger.debug('User not authenticated')
        return JsonResponse({'count': 0})
    
    user = request.user
    notifications = Notification.objects.filter(user=user, viewed=False)
    notifications_count = notifications.count()

    logger.debug(f'User: {user}, Unread notifications: {notifications_count}')
    
    return JsonResponse({'count': notifications_count})

# Создание уведомления о удалении из друзей
def create_remove_friend_notification(from_user, to_user):
    Notification.objects.create(
        user=to_user,
        title='Удаление из друзей',
        body=f'Пользователь {from_user.username} удалил вас из друзей.',
        is_match_notification=False,
        url=reverse('users:user_profile', kwargs={'user_id': from_user.id})
    )

# Создание уведомления о совпадении выбора фильма
def create_match_notification(user, partner, film):
    Notification.objects.create(
        user=partner,
        title='Совпадение по фильму',
        body=f'Вы и {user.username} оба выбрали фильм {film.title}!',
        is_match_notification=True,
        url=reverse('users:film_detail', kwargs={'film_id': film.id})
    )

# Создание уведомления о запросе на выбор фильма
def create_film_selection_request_notification(from_user, to_user):
    Notification.objects.create(
        user=to_user,
        title='Запрос на выбор фильма',
        body=f'Пользователь {from_user.username} хочет выбрать фильм вместе с вами.',
        is_match_notification=False,
        url=reverse('users:preferences', kwargs={'partner_id': from_user.id})
    )

# Создание уведомления о запросе на добавление в друзья
def create_friend_request_notification(from_user, to_user):
    Notification.objects.create(
        user=to_user,
        title='Запрос на добавление в друзья',
        body=f'Пользователь {from_user.username} хочет добавить вас в друзья.',
        is_match_notification=False,
        url=reverse('users:user_profile', kwargs={'user_id': from_user.id})
    )

# Создание уведомления о принятии запроса на добавление в друзья
def create_friend_accept_notification(from_user, to_user):
    Notification.objects.create(
        user=to_user,
        title='Принятие запроса на добавление в друзья',
        body=f'Пользователь {from_user.username} принял ваш запрос на добавление в друзья.',
        is_match_notification=False,
        url=reverse('users:user_profile', kwargs={'user_id': from_user.id})
    )

# Проверка совпадения выбора фильма
def check_for_match(user, partner, film):
    if FilmChoice.objects.filter(user=partner, film=film).exists():
        create_match_notification(user, partner, film)
        create_match_notification(partner, user, film)