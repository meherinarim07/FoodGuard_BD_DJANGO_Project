from django.contrib import messages
from django.db.models import ProtectedError
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Vendor
from .forms import RegisterForm,VendorForm
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

def vendors(request):
    v_list = Vendor.objects.all().order_by('-risk_score')
    return render(request, 'accounts/vendors.html', {'vendors': v_list})


def vendor_detail(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    reports = vendor.foodreport_set.all().order_by('-created_at')
    return render(request, 'accounts/vendor_detail.html', {'vendor': vendor, 'reports': reports})

@role_required('citizen', 'authority')
def vendor_create(request):
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vendor added.')
            return redirect('vendors')
    else:
        form = VendorForm()
    return render(request, 'accounts/vendor_create.html', {'form': form})

@role_required('authority')
def vendor_update(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vendor updated.')
            return redirect('vendors')
    else:
        form = VendorForm(instance=vendor)
    return render(request, 'accounts/vendor_update.html', {'form': form})


@role_required('authority')
def vendor_delete(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        try:
            vendor.delete()
            messages.success(request, 'Vendor deleted.')
        except ProtectedError:
            # reports still point to this vendor (on_delete=PROTECT), so it cannot be deleted
            messages.error(request, 'This vendor has reports, so it cannot be deleted.')
        return redirect('vendors')
    return render(request, 'accounts/vendor_delete.html', {'vendor': vendor})


