from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from accounts_app.decorators import role_required
from reports_app.models import FoodReport
from .models import AreaAlert, Investigation, ResolutionProof
from .forms import InvestigationForm, ResolutionProofForm


def alerts(request):
    a_list = AreaAlert.objects.all().order_by('-is_active', '-created_at')
    return render(request, 'enforcement/alerts.html', {'alerts': a_list})


@role_required('authority')
def alert_deactivate(request, pk):
    alert = get_object_or_404(AreaAlert, pk=pk)
    if request.method == 'POST':
        alert.deactivate()
        messages.success(request, 'Alert deactivated.')
    return redirect('alerts')


@role_required('authority')
def alert_reactivate(request, pk):
    alert = get_object_or_404(AreaAlert, pk=pk)
    if request.method == 'POST':
        if AreaAlert.objects.filter(vendor=alert.vendor, is_active=True).exists():
            messages.error(request, 'This vendor already has an active alert.')
        else:
            alert.is_active = True
            alert.save()
            messages.success(request, 'Alert reactivated.')
    return redirect('alerts')
