from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from accounts_app.decorators import role_required
from .models import FoodReport, Evidence, AwarenessPost
from .forms import FoodReportForm, EvidenceForm, AwarenessPostForm


# ---------- Food reports ----------
def reports(request):
    r_list = FoodReport.objects.all().order_by('-created_at')
    status = request.GET.get('status')
    severity = request.GET.get('severity')
    if status:
        r_list = r_list.filter(status=status)
    if severity:
        r_list = r_list.filter(severity=severity)
    return render(request, 'reports/reports.html', {
        'reports': r_list,
        'status_choices': FoodReport.STATUS_CHOICES,
        'severity_choices': FoodReport.SEVERITY_CHOICES,
        'status': status,
        'severity': severity,
    })


@role_required('citizen')
def my_reports(request):
    r_list = FoodReport.objects.filter(reporter=request.user).order_by('-created_at')
    return render(request, 'reports/my_reports.html', {'reports': r_list})


def report_detail(request, pk):
    report = get_object_or_404(FoodReport, pk=pk)
    chain = report.get_chain()
    return render(request, 'reports/report_detail.html', {
        'report': report,
        'evidence_list': report.evidence_set.all(),
        'verifications': chain['verifications'],
        'investigation': chain['investigation'],
    })


@role_required('citizen')
def report_create(request):
    if request.method == 'POST':
        form = FoodReportForm(request.POST)
        if form.is_valid():
            # same user + same vendor + same food item within 2 days is not allowed
            two_days_ago = timezone.now() - timedelta(days=2)
            existing = FoodReport.objects.filter(
                reporter=request.user, vendor=form.cleaned_data['vendor'],
                food_item__iexact=form.cleaned_data['food_item'].strip(),
                created_at__gte=two_days_ago).first()
            if existing:
                messages.warning(request, 'You already reported this item for this vendor. '
                                          'You can add more photos or details to your existing report.')
                return redirect('report_detail', pk=existing.pk)
            report = form.save(commit=False)
            report.reporter = request.user
            report.save()
            report.submit()
            messages.success(request, 'Report submitted. Please add photo evidence to help the verifiers.')
            return redirect('evidence_create', pk=report.pk)
    else:
        form = FoodReportForm()
    return render(request, 'reports/report_create.html', {'form': form})


@login_required
def report_update(request, pk):
    report = get_object_or_404(FoodReport, pk=pk)
    if report.reporter != request.user or report.status != 'pending':
        messages.error(request, 'Only the reporter can edit a report, and only while it is pending.')
        return redirect('report_detail', pk=pk)
    if request.method == 'POST':
        form = FoodReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, 'Report updated.')
            return redirect('report_detail', pk=pk)
    else:
        form = FoodReportForm(instance=report)
    return render(request, 'reports/report_update.html', {'form': form, 'report': report})


@login_required
def report_delete(request, pk):
    report = get_object_or_404(FoodReport, pk=pk)
    if report.reporter != request.user or report.status != 'pending':
        messages.error(request, 'Only the reporter can delete a report, and only while it is pending.')
        return redirect('report_detail', pk=pk)
    if request.method == 'POST':
        vendor = report.vendor
        report.delete()
        vendor.calculate_risk_score()
        messages.success(request, 'Report deleted.')
        return redirect('my_reports')
    return render(request, 'reports/report_delete.html', {'report': report})


# ---------- Evidence ----------
@login_required
def evidence_create(request, pk):
    report = get_object_or_404(FoodReport, pk=pk)
    if report.reporter != request.user:
        messages.error(request, 'Only the reporter can add evidence to this report.')
        return redirect('report_detail', pk=pk)
    if request.method == 'POST':
        form = EvidenceForm(request.POST, request.FILES)
        if form.is_valid():
            evidence = form.save(commit=False)
            evidence.report = report
            evidence.save()
            messages.success(request, 'Evidence uploaded.')
            return redirect('report_detail', pk=report.pk)
    else:
        form = EvidenceForm()
    return render(request, 'reports/evidence_create.html', {'form': form, 'report': report})


@login_required
def evidence_update(request, pk):
    evidence = get_object_or_404(Evidence, pk=pk)
    if evidence.report.reporter != request.user:
        messages.error(request, 'Only the reporter can edit this evidence.')
        return redirect('report_detail', pk=evidence.report.pk)
    if request.method == 'POST':
        form = EvidenceForm(request.POST, request.FILES, instance=evidence)
        if form.is_valid():
            form.save()
            return redirect('report_detail', pk=evidence.report.pk)
    else:
        form = EvidenceForm(instance=evidence)
    return render(request, 'reports/evidence_update.html', {'form': form, 'evidence': evidence})


@login_required
def evidence_delete(request, pk):
    evidence = get_object_or_404(Evidence, pk=pk)
    report_pk = evidence.report.pk
    if evidence.report.reporter != request.user:
        messages.error(request, 'Only the reporter can delete this evidence.')
        return redirect('report_detail', pk=report_pk)
    if request.method == 'POST':
        evidence.delete()
        return redirect('report_detail', pk=report_pk)
    return render(request, 'reports/evidence_delete.html', {'evidence': evidence})

def awareness(request):
    p_list = AwarenessPost.objects.all().order_by('-published_at')
    return render(request, 'reports/awareness.html', {'posts': p_list})


def post_detail(request, pk):
    post = get_object_or_404(AwarenessPost, pk=pk)
    post.increment_views()
    return render(request, 'reports/post_detail.html', {'post': post})
