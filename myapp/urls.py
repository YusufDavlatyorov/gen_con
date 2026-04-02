from django.urls import path
from .views import (
    TaskListView, 
    TaskDetailView, 
    TaskCreateView, 
    TaskUpdateView, 
    TaskDeleteView,
    CompletedTaskListView,
    accept_task,    # Добавили импорт функции
    complete_task,
    about_view,
    rating_view,
    task_toggle
)

urlpatterns = [
    # Списки задач
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('tasks/completed/', CompletedTaskListView.as_view(), name='completed_tasks'),
    
    # Деталка и CRUD
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('tasks/add/', TaskCreateView.as_view(), name='task_add'),
    path('tasks/<int:pk>/edit/', TaskUpdateView.as_view(), name='task_edit'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    
    # Логика взаимодействия (Action-пути)
    path('tasks/<int:pk>/accept/', accept_task, name='accept_task'),     # Для волонтера
    path('tasks/<int:pk>/complete/', complete_task, name='complete_task'), # Для завершения

    path('about/', about_view, name='about'),
    path('rating/', rating_view, name='rating'),
     path('tasks/<int:pk>/toggle/', task_toggle, name='task_toggle'),
]
