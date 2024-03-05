from django.urls import path
from .views import (
    home,
    partner_selection,
    preferences,
    film_selection,
    result,
    history,
    register,
    confirm_match,
    confirm_match_result,
)
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('home/', home, name='home'),
    path('partner_selection/', partner_selection, name='partner_selection'),
    path('preferences/<int:partner_id>/', preferences, name='preferences'),
    path('film_selection/', film_selection, name='film_selection'),
    path('result/', result, name='result'),
    path('history/', history, name='history'),
    path('register/', register, name='register'),
    path('confirm_match/', confirm_match, name='confirm_match'),
    path('confirm_match_result/<int:film_id>/', confirm_match_result, name='confirm_match_result'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    # Добавьте другие URL-маршруты, как необходимо
]
