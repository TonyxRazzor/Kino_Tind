from django.contrib import admin
from django.urls import path
from django.urls.base import reverse
from django.utils.html import format_html
from .admin_actions import load_data_action
from .admin_actions import load_data_view  # Добавляем импорт
from .models import Film

@admin.register(Film)
class FilmsAdmin(admin.ModelAdmin):
    list_display = ('name', 'kp_rate', 'year', 'get_genres', 'country', 'poster')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'

    def get_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genre.all()])
    get_genres.short_description = 'Genres'

    def load_data_button(self, obj):
        url = reverse('admin:load_data_view')  # Изменяем ссылку на load_data_view
        return format_html('<a class="button" href="{}">Загрузить данные </a>', url)

    load_data_button.short_description = "Загрузить данные "

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('load_data/', self.admin_site.admin_view(load_data_view), name='load_data_view'),  # Изменяем путь и имя
        ]
        return custom_urls + urls
