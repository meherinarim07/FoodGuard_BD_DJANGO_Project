from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from accounts_app.decorators import role_required
from reports_app.models import FoodReport
from .models import Verification, FraudFlag
from .forms import VerificationForm


@role_required('verifier')
def verification_queue(request):
    # reports that still need verifier opinions, except the verifier's own reports
    q_list = FoodReport.objects.filter(status__in=['pending', 'under_review']) \
        .exclude(reporter=request.user).order_by('created_at')
    # most dangerous reports first
    rank = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    q_list = sorted(q_list, key=lambda r: rank[r.severity])
    done = Verification.objects.filter(verifier=request.user).values_list('report_id', flat=True)
    return render(request, 'verification/queue.html', {'reports': q_list, 'done': list(done)})


@role_required('verifier')
def verifications(request):
    v_list = Verification.objects.filter(verifier=request.user).order_by('-created_at')
    return render(request, 'verification/verifications.html', {'verifications': v_list})

@role_required('verifier')
def verification_create(request, pk):
    report = get_object_or_404(FoodReport, pk=pk)
    if report.status not in ['pending', 'under_review']:
        messages.error(request, 'This report is already closed for verification.')
        return redirect('verification_queue')
    if report.reporter == request.user:
        messages.error(request, 'You cannot verify your own report.')
        return redirect('verification_queue')
    if Verification.objects.filter(report=report, verifier=request.user).exists():
        messages.error(request, 'You have already verified this report.')
        return redirect('verification_queue')
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            v = form.save(commit=False)
            v.report = report
            v.verifier = request.user
            v.save()
            report.update_status()
            messages.success(request, 'Your verification was saved.')
            return redirect('verification_queue')
    else:
        form = VerificationForm()
    return render(request, 'verification/verification_create.html', {
        'form': form, 'report': report, 'evidence_list': report.evidence_set.all()})


@role_required('verifier')
def verification_update(request, pk):
    v = get_object_or_404(Verification, pk=pk, verifier=request.user)
    if v.report.status not in ['pending', 'under_review']:
        messages.error(request, 'Opinions cannot be changed after the report is verified or closed.')
        return redirect('verifications')
    if request.method == 'POST':
        form = VerificationForm(request.POST, instance=v)
        if form.is_valid():
            form.save()
            v.report.update_status()
            return redirect('verifications')
    else:
        form = VerificationForm(instance=v)
    return render(request, 'verification/verification_update.html', {'form': form, 'verification': v})


@role_required('verifier')
def verification_delete(request, pk):
    v = get_object_or_404(Verification, pk=pk, verifier=request.user)
    if v.report.status not in ['pending', 'under_review']:
        messages.error(request, 'Opinions cannot be deleted after the report is verified or closed.')
        return redirect('verifications')
    if request.method == 'POST':
        report = v.report
        v.delete()
        report.update_status()
        return redirect('verifications')
    return render(request, 'verification/verification_delete.html', {'verification': v})


@role_required('authority')
def fraud_flags(request):
    f_list = FraudFlag.objects.all().order_by('-created_at')
    return render(request, 'verification/fraud_flags.html', {'flags': f_list})


@role_required('authority')
def fraudflag_resolve(request, pk):
    flag = get_object_or_404(FraudFlag, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['confirmed_fraud', 'dismissed']:
            flag.resolve(new_status)
            messages.success(request, 'Fraud flag resolved.')
        return redirect('fraud_flags')
    return render(request, 'verification/fraudflag_resolve.html', {'flag': flag})
