from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Users, Profile

@receiver(post_save, sender=Users)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Добавляем defaults с начальным рейтингом (например, 0)
        Profile.objects.get_or_create(
            user=instance, 
            defaults={'rating': 0}  # Укажите здесь начальное значение
        )

@receiver(post_save, sender=Users)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
