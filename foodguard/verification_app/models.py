from datetime import timedelta
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from reports_app.models import FoodReport

SPIKE_REASON = 'Possible coordinated attack'


class Verification(models.Model):
    VERDICT_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('unclear', 'Unclear'),
    ]
    report = models.ForeignKey(FoodReport, on_delete=models.CASCADE)
    verifier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='verifications')
    verdict = models.CharField(max_length=20, choices=VERDICT_CHOICES, default='unclear')
    confidence = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    evidence_quality = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # one verifier can verify one report only one time
        constraints = [
            models.UniqueConstraint(fields=['report', 'verifier'], name='unique_verifier_per_report'),
        ]

    def approve(self):
        self.verdict = 'approved'
        self.save()
        self.report.update_status()

    def reject(self):
        self.verdict = 'rejected'
        self.save()
        self.report.update_status()

    def __str__(self):
        return f"{self.verifier.username} -> report {self.report_id} ({self.verdict})"




class FraudFlag(models.Model):
    SUSPICION_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('confirmed_fraud', 'Confirmed fraud'),
        ('dismissed', 'Dismissed'),
    ]
    report = models.ForeignKey(FoodReport, on_delete=models.CASCADE)
    reason = models.CharField(max_length=200)
    suspicion_level = models.CharField(max_length=20, choices=SUSPICION_CHOICES, default='low')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Flag on report {self.report_id} ({self.suspicion_level})"