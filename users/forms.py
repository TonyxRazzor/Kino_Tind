# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from films.models import FilmChoice, Genre, Film


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'phone_number', 'photo', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Phone number'})
        self.fields['photo'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    
class PartnerSelectionForm(forms.Form):
    partner = forms.ModelChoiceField(queryset=User.objects.all(), empty_label="Выберите партнера")


class PreferencesForm(forms.Form):
    genre = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={'max_length': "Можно выбрать не более трех жанров."},
    )

    def update_genre_choices(self, genre_choices):
        self.fields['genre'].choices = [(genre, genre) for genre in genre_choices]

    def update_genre_initial(self, selected_genres):
        self.fields['genre'].initial = selected_genres
    
    def clean_genre(self):
        selected_genres = self.cleaned_data.get('genre', [])
        if len(selected_genres) > 3:
            raise forms.ValidationError("Можно выбрать не более трех жанров.")
        return selected_genres


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

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'photo']

class ProfilePhotoForm(forms.Form):
    photo = forms.ImageField()

class ResultForm(forms.Form):
    # Добавьте поля, если необходимо
    pass

class HistoryForm(forms.Form):
    # Добавьте поля, если необходимо
    pass
