from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q

# Импорты твоих моделей и форм
from .models import Task
from .forms import TaskForm 
from .permissions import RolePermissions
from accounts.models import Profile

# Добавь импорт в начало views.py
from django_filters.views import FilterView
from .filters import TaskFilter

# Измени класс TaskListView
class TaskListView(LoginRequiredMixin, FilterView): # Замени ListView на FilterView
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    filterset_class = TaskFilter # Укажи класс фильтра

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs['request'] = self.request # Передаем request в фильтр для логики в __init__
        return kwargs

    def get_queryset(self):
        user = self.request.user
        # Базовая фильтрация (только активные)
        queryset = Task.objects.filter(is_completed=False).select_related('client', 'volunteer')
        
        if user.is_superuser:
            return queryset
        elif user.is_volunteer:
            return queryset.filter(Q(volunteer=user) | Q(volunteer__isnull=True))
        elif user.is_client:
            return queryset.filter(client=user)
        return queryset.none()


# 2. СПИСОК ВЫПОЛНЕННЫХ ЗАДАЧ (Архив)
class CompletedTaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/completed_tasks.html'
    context_object_name = 'completed_tasks'

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(is_completed=True).select_related('client', 'volunteer')
        
        if user.is_superuser:
            return queryset
        # Показываем задачи, где пользователь был либо клиентом, либо волонтером
        return queryset.filter(Q(client=user) | Q(volunteer=user))

# 3. СОЗДАНИЕ ЗАДАЧИ
class TaskCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')

    def test_func(self):
        # Проверка прав: может ли юзер добавлять (is_client или is_superuser)
        return RolePermissions.can_add_task(self.request.user)

    def form_valid(self, form):
        # Автоматически привязываем текущего юзера как КЛИЕНТА
        form.instance.client = self.request.user
        return super().form_valid(form)  

# 4. РЕДАКТИРОВАНИЕ
class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')

    def test_func(self):
        # Только владелец-клиент или админ
        return RolePermissions.can_edit_task(self.request.user, self.get_object())

# 5. ФУНКЦИЯ: ПРИНЯТЬ ЗАДАЧУ (ДЛЯ ВОЛОНТЕРОВ)
def accept_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Проверяем через permissions.py (is_volunteer=True и volunteer=None)
    if RolePermissions.can_accept_task(request.user, task):
        task.volunteer = request.user
        task.save()
    return redirect('task_list')

# 6. ФУНКЦИЯ: ЗАВЕРШИТЬ ЗАДАЧУ
def complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if RolePermissions.can_complete_task(request.user, task):
        task.is_completed = True
        task.save() # Сработает сигнал на начисление рейтинга
    return redirect('task_list')

# 7. ДЕТАЛЬНЫЙ ПРОСМОТР
class TaskDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def test_func(self):
        return RolePermissions.can_view_task(self.request.user, self.get_object())

# 8. УДАЛЕНИЕ ЗАДАЧИ
class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')

    def test_func(self):
        return RolePermissions.can_delete_task(self.request.user, self.get_object())

# 9. СТАТИЧЕСКИЕ СТРАНИЦЫ
def about_view(request):
    return render(request, 'tasks/about.html')

def rating_view(request):
    # Оптимизированный запрос рейтинга ТОП-10
    top_volunteers = Profile.objects.filter(
        user__is_volunteer=True
    ).select_related('user').order_by('-rating')[:10]
    
    return render(request, 'tasks/rating.html', {'volunteers': top_volunteers})

def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Если задача была выполнена, делаем её активной, и наоборот
    task.is_completed = not task.is_completed
    task.save()
    return redirect('task_list')

from django.core.mail import send_mail # Не забудьте импорт!

def accept_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if RolePermissions.can_accept_task(request.user, task):
        task.volunteer = request.user
        task.save()
        
        # Данные для писем
        client_email = task.client.email
        volunteer_email = task.volunteer.email
        task_title = task.title

        # 1. Письмо Клиенту
        send_mail(
            subject='Помощь уже в пути!',
            message=f'Здравствуйте! Волонтер {task.volunteer.username} принял вашу задачу "{task_title}". Скоро он с вами свяжется.',
            from_email=None,
            recipient_list=[client_email],
            fail_silently=True,
        )

        # 2. Письмо Волонтеру
        send_mail(
            subject='Вы приняли новую задачу!',
            message=f'Вы успешно приняли задачу "{task_title}". Спасибо за помощь! Свяжитесь с клиентом: {task.client.username} ({client_email}).',
            from_email=None,
            recipient_list=[volunteer_email],
            fail_silently=True,
        )
        
    return redirect('task_list')


import requests
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

def ai_advisor_view(request):
    return render(request, 'tasks/ai_advisor.html')

@require_POST
def ai_chat_view(request):
    data = json.loads(request.body)
    messages = data.get('messages', [])
    system_prompt = data.get('system_prompt', '')

    response = requests.post(
        'https://openrouter.ai/api/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {settings.OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
        },
        json={
            'model': 'google/gemini-2.0-flash-001',
            'max_tokens': 700,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                *messages
            ]
        }
    )

    result = response.json()
    reply = result['choices'][0]['message']['content']
    return JsonResponse({'reply': reply})