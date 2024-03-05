from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ('username', 'phone_number')
    search_fields = ('username', 'phone_number')
    list_filter = ('username',)
    ordering = ('username', )
    empty_value_display = '-пусто-'
