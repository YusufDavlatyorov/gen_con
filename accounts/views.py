from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .forms import (
    RegistrationForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ProfileForm,
    UserUpdateForm
)
from .models import Users, Profile


# =========================
# REGISTER
# =========================
def register_view(request):
    if request.method == 'POST':
        # 1. Берем данные из POST
        data = request.POST.copy()
        
        # 2. Переводим "role" из HTML в поля модели
        role = data.get('role')
        if role == 'volunteer':
            data['is_volunteer'] = True
            data['is_client'] = False
        elif role == 'client':
            data['is_volunteer'] = False
            data['is_client'] = True

        # 3. Передаем уже исправленные данные в форму
        form = RegistrationForm(data)

        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            
            # Сразу логиним пользователя (Session)
            login(request, user)
            messages.success(request, "WELCOME!")
            return redirect('profile')
        else:
            # Если не создается — посмотри в консоль VS Code, там будут ошибки
            print("ОШИБКИ ФОРМЫ:", form.errors) 
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})



# =========================
# LOGIN
# =========================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    error_message = None

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # SESSION
                request.session['username'] = user.username
                request.session['user_id'] = user.id

                # мягкое уведомление (НЕ блокирует)
                if not user.is_email_verified:
                    messages.warning(request, "EMAIL NOT VERIFIED")

                return redirect('profile')
            else:
                error_message = "INVALID USERNAME OR PASSWORD"
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'error_message': error_message
    })


# =========================
# LOGOUT
# =========================
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login')


# =========================
# PROFILE
# =========================
@login_required
def profile_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    return render(request, 'accounts/profile.html', {
        'user': user,
        'profile': profile
    })


# =========================
# EDIT PROFILE
# =========================
@login_required
def edit_profile_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, "PROFILE UPDATED")
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


# =========================
# FORGOT PASSWORD
# =========================
def forgot_password_view(request):
    message = None

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')

            user = Users.objects.filter(email=email).first()

            if user:
                token = user.generate_reset_password_token()
                print(f"DEBUG: /reset-password/{token}/")

            message = "CHECK YOUR EMAIL"
    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/forgot_password.html', {
        'form': form,
        'message': message
    })


# =========================
# RESET PASSWORD
# =========================
def reset_password_confirm_view(request, token):
    user = Users.objects.filter(reset_password_token=token).first()

    if not user or not user.reset_password_token_is_valid():
        return render(request, 'accounts/error.html', {
            'error': 'TOKEN INVALID OR EXPIRED'
        })

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)

        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')

            user.set_password(new_password)
            user.clear_reset_password_token()
            user.save()

            messages.success(request, "PASSWORD UPDATED")
            return redirect('login')
    else:
        form = ResetPasswordForm()

    return render(request, 'accounts/reset_password.html', {
        'form': form
    })


# =========================
# EMAIL CONFIRM (optional)
# =========================
def confirm_email_view(request, token):
    user = Users.objects.filter(email_verification_token=token).first()

    if user and user.email_verification_token_is_valid():
        user.confirm_email()
        return render(request, 'accounts/email_confirmed.html')
    else:
        return render(request, 'accounts/error.html', {
            'error': 'INVALID OR EXPIRED LINK'
        })


# =========================
# AJAX PROFILE UPDATE (JS)
# =========================
@login_required
def update_profile(request):
    if request.method == "POST":
        try:
            user = request.user
            profile, _ = Profile.objects.get_or_create(user=user)

            # 1. Читаем текстовые данные из request.POST (а не из body)
            user.username = request.POST.get("username", user.username)
            user.region = request.POST.get("region", user.region)
            
            profile.full_name = request.POST.get("full_name", profile.full_name)
            profile.age = request.POST.get("age") or profile.age
            profile.bio = request.POST.get("bio", profile.bio)

            # 2. Читаем ФОТО из request.FILES
            if 'image' in request.FILES:
                profile.image = request.FILES['image']

            user.save()
            profile.save()

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            })

    return JsonResponse({"success": False}, status=400)


