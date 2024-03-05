from django.urls import path
from .admin_actions import load_data_action

urlpatterns = [
    path('admin/load_data/', load_data_action, name='load_data_action'),
]

# # Вариант 2
# urlpatterns = [
#     path('load_data/', load_data_view, name='load_data_action'),
# ]