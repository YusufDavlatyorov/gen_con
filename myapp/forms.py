from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        # Добавили address и phone в список полей
        fields = ['title', 'description', 'address', 'phone', 'deadline', 'is_completed']
        
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Введите название...', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Описание...', 'class': 'form-control'}),
            'address': forms.TextInput(attrs={'placeholder': 'Укажите адрес...', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': '+992 (___) ___ __ __', 'class': 'form-control'}),
            'deadline': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            ),
            'is_completed': forms.CheckboxInput(attrs={'class': 'glass-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['deadline'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
