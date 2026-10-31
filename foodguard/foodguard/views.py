from django.shortcuts import render


def home(request):
    return render(request,'foodguard/home.html')