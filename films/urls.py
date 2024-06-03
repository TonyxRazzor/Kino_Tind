from django.urls import path
from .admin_actions import load_data_action
from users import views

app_name = 'films'

urlpatterns = [
    path('admin/load_data/', load_data_action, name='load_data_action'),
    path('<int:film_id>/', views.film_detail, name='film_detail'),
]
