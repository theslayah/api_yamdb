from django.contrib import admin

from .models import User


class AdminUser(admin.ModelAdmin):
    """Настройка админки для пользователей."""
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'bio', 'role', 'confirmation_code')
    search_fields = ('username',)
    list_filter = ('role',)
    empty_value_display = '-пусто-'


admin.site.register(User, AdminUser)
