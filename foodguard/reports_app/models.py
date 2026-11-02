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

    def __str__(self):
        return f"{self.food_item} @ {self.vendor.shop_name}"