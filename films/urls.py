from django.urls import path
from .admin_actions import load_data_action, export_data_action_250, export_data_action_1000
from users import views

app_name = 'films'

urlpatterns = [
    path('admin/load_data/', load_data_action, name='load_data_action'),
    path('admin/export-data-250/', export_data_action_250, name='export_data_action_250'),
    path('admin/export-data-1000/', export_data_action_1000, name='export_data_action_1000'),
    path('<int:film_id>/', views.film_detail, name='film_detail'),
]
