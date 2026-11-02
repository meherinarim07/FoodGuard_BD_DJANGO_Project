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


@role_required('authority')
def investigations(request):
    i_list = Investigation.objects.all().order_by('-opened_at')
    # verified reports that nobody is investigating yet
    waiting = FoodReport.objects.filter(status='verified', investigation__isnull=True)
    return render(request, 'enforcement/investigations.html',
                  {'investigations': i_list, 'waiting': waiting})


@role_required('authority')
def investigation_detail(request, pk):
    inv = get_object_or_404(Investigation, pk=pk)
    return render(request, 'enforcement/investigation_detail.html',
                  {'investigation': inv, 'proofs': inv.resolutionproof_set.all()})

@role_required('authority')
def investigation_create(request, pk):
    report = get_object_or_404(FoodReport, pk=pk)
    if report.status != 'verified':
        messages.error(request, 'Only a verified report can be investigated.')
        return redirect('investigations')
    if Investigation.objects.filter(report=report).exists():
        messages.error(request, 'This report already has an investigation.')
        return redirect('investigations')
    if request.method == 'POST':
        form = InvestigationForm(request.POST)
        if form.is_valid():
            inv = form.save(commit=False)
            inv.report = report
            inv.authority = request.user
            inv.save()
            messages.success(request, 'Investigation opened.')
            return redirect('investigation_detail', pk=inv.pk)
    else:
        form = InvestigationForm()
    return render(request, 'enforcement/investigation_create.html', {'form': form, 'report': report})


@role_required('authority')
def investigation_update(request, pk):
    inv = get_object_or_404(Investigation, pk=pk)
    if request.method == 'POST':
        form = InvestigationForm(request.POST, instance=inv)
        if form.is_valid():
            form.save()
            return redirect('investigation_detail', pk=pk)
    else:
        form = InvestigationForm(instance=inv)
    return render(request, 'enforcement/investigation_update.html', {'form': form, 'investigation': inv})