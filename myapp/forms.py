from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'is_completed']
        
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Введите название...', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Описание...'}),
            'deadline': forms.DateTimeInput(
                # Формат ISO важен для корректной работы datetime-local
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
        # Добавляем форматы, которые Django будет пробовать применить к строке из браузера
        self.fields['deadline'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']

