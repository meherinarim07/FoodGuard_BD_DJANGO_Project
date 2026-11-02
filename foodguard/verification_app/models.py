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

    @staticmethod
    def evaluate(report):
        # the system checks every new report and raises a flag when something looks suspicious
        now = timezone.now()
        vendor = report.vendor

        # 1. vendor spike: far more reports in 24 hours than this vendor normally gets
        last_day = FoodReport.objects.filter(
            vendor=vendor, created_at__gte=now - timedelta(hours=24)).count()
        before = FoodReport.objects.filter(
            vendor=vendor, created_at__gte=now - timedelta(days=8),
            created_at__lt=now - timedelta(hours=24)).count()
        daily_average = before / 7
        spike_open = FraudFlag.objects.filter(
            report__vendor=vendor, status='open', reason__startswith=SPIKE_REASON).exists()
        if last_day >= 30 and last_day > 5 * daily_average and not spike_open:
            return FraudFlag.objects.create(
                report=report, suspicion_level='high',
                reason=f'{SPIKE_REASON}: {last_day} reports in 24 hours (normal is about {daily_average:.0f} per day)')

        # 2. one user sending too many reports
        reporter = report.reporter
        recent = FoodReport.objects.filter(
            reporter=reporter, created_at__gte=now - timedelta(hours=1)).count()
        if recent >= 4:
            return FraudFlag.objects.create(
                report=report, suspicion_level='high',
                reason=f'Reporter sent {recent} reports within one hour')

        # 3. reporter with many rejected reports
        rejected = FoodReport.objects.filter(reporter=reporter, status='rejected').count()
        if rejected >= 3:
            return FraudFlag.objects.create(
                report=report, suspicion_level='medium',
                reason=f'Reporter already has {rejected} rejected reports')
        return None

    def resolve(self, new_status):
        self.status = new_status
        self.save()
        vendor = self.report.vendor
        if new_status == 'confirmed_fraud':
            if self.reason.startswith(SPIKE_REASON):
                # attack confirmed: reject every unchecked report of the last 24 hours
                since = timezone.now() - timedelta(hours=24)
                unchecked = FoodReport.objects.filter(
                    vendor=vendor, created_at__gte=since, status__in=['pending', 'under_review'])
                for r in unchecked:
                    r.update_status('rejected')
            else:
                self.report.update_status('rejected')
        else:
            # dismissed: the spike was real, so alerts can start again
            vendor.calculate_risk_score()
            vendor.check_alert()


    def __str__(self):
        return f"Flag on report {self.report_id} ({self.suspicion_level})"