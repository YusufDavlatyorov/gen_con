from django.core.exceptions import PermissionDenied

class RolePermissions:
    """
    Финальная логика ролей. Используем флаги модели Users.
    """

    @staticmethod
    def can_view_task(user, task):
        if not user.is_authenticated: return False
        if user.is_superuser: return True
        # Видит автор, исполнитель или волонтер, если задача вакантна
        return (user == task.client or 
                user == task.volunteer or 
                (user.is_volunteer and task.volunteer is None))

    @staticmethod
    def can_add_task(user):
        # Только клиенты и админы могут создавать
        return user.is_authenticated and (user.is_superuser or user.is_client or user.is_volunteer)

    @staticmethod
    def can_edit_task(user, task):
        if not user.is_authenticated: return False
        if user.is_superuser: return True
        # Редактирует только автор-клиент
        return user.is_client and task.client == user

    @staticmethod
    def can_delete_task(user, task):
        if not user.is_authenticated: return False
        if user.is_superuser: return True
        # Удаляет автор, если задача не завершена
        return user.is_client and task.client == user and not task.is_completed

    @staticmethod
    def can_accept_task(user, task):
        """
        Логика для кнопки 'Помочь':
        Пропускает, если пользователь волонтер (или админ) и задача СВОБОДНА.
        """
        if not user.is_authenticated: return False
        
        is_power_user = user.is_volunteer or user.is_superuser
        # Задача должна быть без волонтера (None)
        return is_power_user and task.volunteer is None

    @staticmethod
    def can_complete_task(user, task):
        """
        Логика для кнопки 'Готово':
        Завершить может только тот волонтер, который её взял, или админ.
        """
        if not user.is_authenticated: return False
        if user.is_superuser: return True
        
        return user.is_volunteer and task.volunteer == user
