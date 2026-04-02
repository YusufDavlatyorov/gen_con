from django import forms
from .models import Users, Profile
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


# =========================
# REGISTRATION
# =========================
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password"
    )

    class Meta:
        model = Users
        fields = ['username', 'email', 'password', 'is_volunteer', 'is_client', 'region']

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()

        if len(username) < 4:
            raise forms.ValidationError('Username too short')

        if Users.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already taken')

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()

        if Users.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists')

        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')

        try:
            validate_password(password)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)

        return password

    def clean(self):
        cleaned_data = super().clean()

        is_volunteer = cleaned_data.get('is_volunteer')
        is_client = cleaned_data.get('is_client')

        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')

        # роли
        if is_volunteer and is_client:
            raise forms.ValidationError("Choose only one role")

        if not is_volunteer and not is_client:
            raise forms.ValidationError("Choose a role")

        # пароли
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.username = user.username.strip()
        user.email = user.email.lower()

        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user


# =========================
# LOGIN
# =========================
class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )


# =========================
# FORGOT PASSWORD
# =========================
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Email"
    )

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()

        if not Users.objects.filter(email=email).exists():
            raise forms.ValidationError("User not found")

        return email


# =========================
# RESET PASSWORD
# =========================
class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password"
    )

    def clean(self):
        cleaned_data = super().clean()

        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")

        if p1 and len(p1) < 8:
            raise forms.ValidationError("Password too short")

        return cleaned_data


# =========================
# PROFILE UPDATE
# =========================


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        # Указываем поля, которые пользователь может редактировать
        # Поле 'user' обычно исключают, так как оно привязывается автоматически
        fields = ['full_name', 'age', 'image', 'bio', 'rating']
        
        # Добавляем красивые виджеты или стили (опционально)
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ФИО'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'full_name': 'Полное имя',
            'image': 'Аватар',
            'bio': 'О себе',
            'rating': 'Рейтинг',
        }


# =========================
# USER UPDATE (optional)
# =========================
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['email', 'region', 'telegram_id']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram_id': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()

        qs = Users.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Email already used")

        return email