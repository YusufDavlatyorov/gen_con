from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users, Profile

# Отображение профиля внутри страницы пользователя
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль пользователя'
    fields = ('full_name', 'age', 'rating', 'image', 'bio')

@admin.register(Users)
class MyUserAdmin(admin.ModelAdmin):
    # Что отображать в списке всех пользователей
    list_display = ('username', 'email', 'role', 'region', 'is_email_verified', 'is_active', 'date_joined')
    
    # Фильтры справа
    list_filter = ('is_volunteer', 'is_client', 'is_staff', 'is_email_verified', 'region')
    
    # Поля поиска
    search_fields = ('username', 'email', 'telegram_id')
    
    # Группировка полей при редактировании
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('email', 'telegram_id', 'region')}),
        ('Роли и Доступ', {'fields': ('is_volunteer', 'is_client', 'is_active', 'is_staff', 'is_superuser')}),
        ('Безопасность (Токены)', {
            'classes': ('collapse',), # Скрываем по умолчанию
            'fields': ('is_email_verified', 'email_verification_token', 'reset_password_token')
        }),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    
    # Подключаем профиль
    inlines = (ProfileInline,)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'rating', 'age', 'created_at')
    search_fields = ('user__username', 'full_name')
    list_filter = ('rating', 'created_at')
