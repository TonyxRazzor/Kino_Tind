# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from films.models import FilmChoice, Genre, Film


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('phone_number', 'photo')


class PartnerSelectionForm(forms.Form):
    partner = forms.ModelChoiceField(queryset=User.objects.all(), empty_label="Выберите партнера")


class PreferencesForm(forms.Form):
    genre = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    def update_genre_choices(self, genre_choices):
        self.fields['genre'].choices = [(genre, genre) for genre in genre_choices]

    def update_genre_initial(self, selected_genres):
        self.fields['genre'].initial = selected_genres


class FilmSelectionForm(forms.Form):
    genre = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )


class FilmChoiceForm(forms.ModelForm):
    genre = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = FilmChoice
        fields = ['film', 'genre']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['film'].queryset = Film.objects.all()  # Установка queryset для поля film

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()  # Сохранение ManyToMany связей
        return instance



class ResultForm(forms.Form):
    # Добавьте поля, если необходимо
    pass

class HistoryForm(forms.Form):
    # Добавьте поля, если необходимо
    pass
