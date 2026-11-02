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