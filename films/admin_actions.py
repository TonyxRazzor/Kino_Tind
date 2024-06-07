from django import forms
from django.shortcuts import redirect
from django.http import HttpResponse
from django.shortcuts import render
from films.load_data import load_data_script
from films.views import SEARCH
from django.contrib import messages

class LoadDataForm(forms.Form):
    # Вы можете добавить поля формы, если это необходимо
    pass

class ExportDataForm(forms.Form):
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


def export_data_action_250(request, queryset=None):
    form = ExportDataForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        result = SEARCH.get_top_movies('54023ee1-c992-4bfa-b48e-f2e7a6a2b7a4')
        if result == "success":
            messages.success(request, 'Данные успешно выгружены в JSON.')
        else:
            messages.error(request, f'Ошибка при выгрузке данных <<action_250>>: {result}')
        return redirect('admin:films_film_changelist')

    return render(request, 'admin/export_data_view.html', {'app_label': 'films', 'form': form})


export_data_action_250.short_description = "Выгрузить данные <<TOP-250>> в JSON"

def export_data_action_1000(request, queryset=None):
    form = ExportDataForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        result = SEARCH.get_popular_movies('54023ee1-c992-4bfa-b48e-f2e7a6a2b7a4')
        if result == "success":
            messages.success(request, 'Данные успешно выгружены в JSON.')
        else:
            messages.error(request, f'Ошибка при выгрузке данных <<action_1000>>: {result}')
        return redirect('admin:films_film_changelist')

    return render(request, 'admin/export_data_view.html', {'app_label': 'films', 'form': form})


export_data_action_1000.short_description = "Выгрузить данные <<TOP-Popular>> в JSON"