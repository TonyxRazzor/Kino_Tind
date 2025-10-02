from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (accept_friend_request, check_notifications,
                    check_user_match, confirm_match, confirm_match_result,
                    film_detail, film_selection, home_view, partner_selection,
                    preferences, register, remove_friend, search_users,
                    send_film_invitation, send_friend_request, user_profile)

app_name = 'users'

urlpatterns = [
    # path('home/', home, name='home'),
    path('partner_selection/', partner_selection, name='partner_selection'),
    path('preferences/<int:partner_id>/', preferences, name='preferences'),
    path('film_selection/', film_selection, name='film_selection'),
    path('register/', register, name='register'),
    path('confirm_match/', confirm_match, name='confirm_match'),
    path('confirm_match_result/<int:film_id>/', confirm_match_result, name='confirm_match_result'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('notifications/check/', check_notifications, name='check_notifications'),
    path('check_match/', check_user_match, name='check_user_match'),
    path('profile/<int:user_id>/', user_profile, name='user_profile'),
    path('send_friend_request/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>/', accept_friend_request, name='accept_friend_request'),
    path('search/', search_users, name='search_users'),
    path('remove_friend/<int:friend_id>/', remove_friend, name='remove_friend'),
    path('send_film_invitation/<int:user_id>/', send_film_invitation, name='send_film_invitation'),
    path('film/<int:film_id>/', film_detail, name='film_detail'),
    path('home/', home_view, name='home'),

    # Добавьте другие URL-маршруты, как необходимо
]
