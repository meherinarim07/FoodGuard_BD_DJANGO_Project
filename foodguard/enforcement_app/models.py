from django.conf import settings
from django.db import models
from django.utils import timezone
from accounts_app.models import Vendor
from reports_app.models import FoodReport


class AreaAlert(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    area = models.CharField(max_length=100)
    risk_score_at_trigger = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def deactivate(self):
        self.is_active = False
        self.save()

    @staticmethod
    def alerts_for(user):
        # active alerts in the area of this user
        area = user.userprofile.area
        return AreaAlert.objects.filter(is_active=True, area__iexact=area)

    def __str__(self):
        return f"Alert: {self.vendor.shop_name} ({self.area})"

class Investigation(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In progress'),
        ('closed', 'Closed'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    report = models.OneToOneField(FoodReport, on_delete=models.CASCADE)
    authority = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='investigations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    action_taken = models.TextField(blank=True)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)  # empty while the investigation is still open

    def open(self):
        self.status = 'open'
        self.closed_at = None
        self.save()
        if self.report.status == 'resolved':
            self.report.update_status('verified')

    def close(self):
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save()
        self.report.update_status('resolved')

    def __str__(self):
        return f"Investigation of report {self.report_id} ({self.status})"


class ResolutionProof(models.Model):
    investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE)
    proof_file = models.FileField(upload_to='proofs/')
    notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proof for investigation {self.investigation_id}"
