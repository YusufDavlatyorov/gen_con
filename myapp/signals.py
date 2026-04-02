from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task

@receiver(post_save, sender=Task)
def update_user_rating(sender, instance, created, **kwargs):
    """
    Начисляем рейтинг волонтеру, если задача помечена как выполненная.
    """
    # Если задача отмечена как выполненная и у неё назначен волонтер
    if instance.is_completed and instance.volunteer:
        # Пытаемся получить профиль волонтера
        # Используем related_name из вашей модели Profile (обычно profile или accounts_profile)
        profile = getattr(instance.volunteer, 'accounts_profile', None) or getattr(instance.volunteer, 'profile', None)
        
        if profile:
            # Начисляем +10 волонтеру за помощь
            profile.rating += 10
            profile.save()

@receiver(post_save, sender=Task)
def notify_client_on_completion(sender, instance, created, **kwargs):
    """
    Здесь можно добавить логику уведомления клиента, 
    когда волонтер завершил его задачу.
    """
    if instance.is_completed:
        print(f"Уведомление: Задача '{instance.title}' для клиента {instance.client.username} завершена!")
