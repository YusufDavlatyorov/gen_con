import django_filters
from .models import Task
from django import forms
from accounts.models import Users

class TaskFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        lookup_expr='icontains', 
        label="Поиск по названию",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Найти задачу...'})
    )
    
    is_free = django_filters.BooleanFilter(
        field_name='volunteer', 
        lookup_expr='isnull', 
        label="Только свободные",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    client = django_filters.ModelChoiceFilter(
        queryset=Users.objects.filter(is_client=True), # ИСПРАВЛЕНО
        label="Клиент",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    volunteer = django_filters.ModelChoiceFilter(
        queryset=Users.objects.filter(is_volunteer=True), # ИСПРАВЛЕНО
        label="Волонтер",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Task
        fields = ['title', 'client', 'volunteer']

    def __init__(self, *args, **kwargs):
        # Важно: достаем request безопасно
        self.user = kwargs.pop('request', None).user if 'request' in kwargs else None
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Если не админ — удаляем выбор других пользователей
            if not self.user.is_superuser:
                if 'client' in self.filters: self.filters.pop('client')
                if 'volunteer' in self.filters: self.filters.pop('volunteer')
            
            # Если клиент — удаляем фильтр "свободные задачи"
            if self.user.is_client and 'is_free' in self.filters:
                self.filters.pop('is_free')
