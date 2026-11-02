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
