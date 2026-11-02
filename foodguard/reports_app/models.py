from django.conf import settings
from django.db import models
from django.utils import timezone
from accounts_app . models import Vendor

class AwarenessPost(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='awareness_posts')
    title = models.CharField(max_length=150)
    content = models.TextField()
    category = models.CharField(max_length=50)
    image = models.ImageField(upload_to='awareness/', blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(default=timezone.now)

    def publish(self):
        self.published_at = timezone.now()
        self.save()

    def increment_views(self):
        self.views_count += 1
        self.save()

    def __str__(self):
        return self.title





class FoodReport(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under review'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('resolved', 'Resolved'),
    ]
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='food_reports')
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    food_item = models.CharField(max_length=100)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


    def submit(self):
        # called once when a citizen sends a new report.
        # The report starts as pending and does not change the vendor risk yet.
        from verification_app.models import FraudFlag
        self.status = 'pending'
        self.save()
        FraudFlag.evaluate(self)

    def update_status(self, new_status=None):
        # with a value: set it directly (authority use)
        # without a value: decide from the verifier votes (2 approvals = verified, 2 rejections = rejected)
        if new_status:
            self.status = new_status
        else:
            approved = self.verification_set.filter(verdict='approved').count()
            rejected = self.verification_set.filter(verdict='rejected').count()
            if approved >= 2:
                self.status = 'verified'
            elif rejected >= 2:
                self.status = 'rejected'
            elif self.verification_set.exists():
                self.status = 'under_review'
            else:
                self.status = 'pending'
        self.save()
        self.reporter.userprofile.calculate_trust_score()
        self.vendor.calculate_risk_score()
        self.vendor.check_alert()

    def get_chain(self):
        # the full life of a report: report -> verifications -> investigation
        try:
            investigation = self.investigation
        except Exception:
            investigation = None
        return {
            'report': self,
            'verifications': self.verification_set.all(),
            'investigation': investigation,
        }

    def __str__(self):
        return f"{self.food_item} @ {self.vendor.shop_name}"



