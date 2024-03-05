from django import forms
from django.shortcuts import redirect
from django.http import HttpResponse
from django.shortcuts import render
from .load_data import load_data_script
from django.contrib import messages

class LoadDataForm(forms.Form):
    # Вы можете добавить поля формы, если это необходимо
    pass

def load_data_action(request, queryset=None):
    form = LoadDataForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        load_data_script()
        # Добавим сообщение для пользователя
        messages.success(request, 'Данные успешно загружены в базу данных.')
        # Перенаправим пользователя на страницу изменения списка фильмов
        return redirect('admin:films_film_changelist')

    return render(request, 'admin/load_data_view.html', {'app_label': 'films', 'form': form})

load_data_action.short_description = "Загрузить данные из скрипта"

def load_data_view(request):
    if request.method == 'POST':
        load_data_script()
        # Перенаправляем пользователя после успешного выполнения скрипта
        return redirect('admin:films_film_changelist')
    return render(request, 'admin/load_data_view.html', {'app_label': 'films'})  # Изменяем 'app_label': 'films' на нужные данные
