from django.contrib import messages
from django.db.models import ProtectedError
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Vendor
from .forms import RegisterForm
from .decorators import role_required


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.userprofile
            profile.phone = form.cleaned_data['phone']
            profile.area = form.cleaned_data['area']
            profile.save()
            login(request, user)
            messages.success(request, 'Welcome to FoodGuard BD! Your account is ready.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    if request.method == 'POST':
        logout(request)
    return redirect('home')