from django.db import models
from accounts.models import Users  

class Task(models.Model):
    client = models.ForeignKey(
        Users, 
        on_delete=models.CASCADE, 
        related_name='created_tasks', 
        verbose_name="Клиент"
    )
    

    volunteer = models.ForeignKey(
        Users, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='helped_tasks', 
        verbose_name="Волонтер"
    )
    
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    
    is_completed = models.BooleanField(default=False, verbose_name="Выполнено")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True, verbose_name="Дедлайн")

    address = models.CharField(max_length=255, verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")


    class Meta:
        ordering = ['-created_at']
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    def __str__(self):
        v_name = self.volunteer.username if self.volunteer else "ожидает"
        return f"{self.title} (Клиент: {self.client.username}, Волонтер: {v_name})"



