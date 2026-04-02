import uuid
from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UsersManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')

        email = self.normalize_email(email)
        username = username.strip()

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_email_verified', True)

        return self.create_user(username, email, password, **extra_fields)


class Users(AbstractBaseUser, PermissionsMixin):
    @property
    def role(self):
        if self.is_superuser:
            return 'superadmin'
        if self.is_volunteer:
            return 'volunteer'
        if self.is_client:
            return 'client'
        return None

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    is_email_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # роли
    is_volunteer = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)

    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    region = models.CharField(max_length=100, blank=True, null=True)

    # токены
    email_verification_token = models.CharField(max_length=100, null=True, blank=True)
    email_verification_token_created_at = models.DateTimeField(null=True, blank=True)

    reset_password_token = models.CharField(max_length=100, null=True, blank=True)
    reset_password_token_created_at = models.DateTimeField(null=True, blank=True)

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UsersManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def save(self, *args, **kwargs):
        if self.is_volunteer and self.is_client:
            raise ValueError("User cannot be both volunteer and client")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    # ===== EMAIL =====
    def generate_email_verification_token(self):
        self.email_verification_token = str(uuid.uuid4())
        self.email_verification_token_created_at = timezone.now()
        self.save()
        return self.email_verification_token

    def email_verification_token_is_valid(self):
        if not self.email_verification_token_created_at:
            return False
        return timezone.now() < self.email_verification_token_created_at + timedelta(hours=24)

    def confirm_email(self):
        self.is_email_verified = True
        self.email_verification_token = None
        self.email_verification_token_created_at = None
        self.save()

    # ===== RESET PASSWORD =====
    def generate_reset_password_token(self):
        self.reset_password_token = str(uuid.uuid4())
        self.reset_password_token_created_at = timezone.now()
        self.save()
        return self.reset_password_token

    def reset_password_token_is_valid(self):
        if not self.reset_password_token_created_at:
            return False
        return timezone.now() < self.reset_password_token_created_at + timedelta(hours=1)

    def clear_reset_password_token(self):
        self.reset_password_token = None
        self.reset_password_token_created_at = None
        self.save()


# =========================
# PROFILE (дополнение!)
# =========================

class Profile(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='accounts_profile')
    full_name = models.CharField(max_length=255, blank=True)
    age = models.IntegerField(null=True, blank=True)
    image=models.ImageField(blank=True,upload_to='avatars/')
    bio = models.TextField(blank=True)
    rating=models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"