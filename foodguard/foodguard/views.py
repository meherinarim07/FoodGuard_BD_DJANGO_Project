from django.shortcuts import render
from accounts_app.models import Vendor
from reports_app.models import FoodReport, AwarenessPost
from enforcement_app.models import AreaAlert


def home(request):
    context = {
        'total_reports': FoodReport.objects.count(),
        'verified_reports': FoodReport.objects.filter(status__in=['verified', 'resolved']).count(),
        'total_vendors': Vendor.objects.count(),
        'active_alerts': AreaAlert.objects.filter(is_active=True).count(),
        'posts': AwarenessPost.objects.all().order_by('-published_at')[:3],
    }
    if request.user.is_authenticated:
        context['my_alerts'] = AreaAlert.alerts_for(request.user)
    return render(request,'foodguard/home.html',context)