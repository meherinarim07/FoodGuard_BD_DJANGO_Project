from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


# Create your models here.
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('verifier', 'Verifier'),
        ('authority', 'Authority'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
    phone = models.CharField(max_length=20, blank=True)
    area = models.CharField(max_length=100, blank=True)
    trust_score = models.FloatField(default=50)
    join_date = models.DateField(auto_now_add=True)

    def calculate_trust_score(self):
        # start at 50, +5 for every verified report, -10 for every rejected report
        reports = self.user.food_reports.all()
        verified = reports.filter(status__in=['verified', 'resolved']).count()
        rejected = reports.filter(status='rejected').count()
        score = 50 + verified * 5 - rejected * 10
        self.trust_score = max(0, min(100, score))
        self.save()
        return self.trust_score

    def get_weight(self):
        # how much this user's reports count: trust score / 50, between 0.3 and 1.5
        weight = max(0.3, min(1.5, self.trust_score / 50))
        # accounts younger than 3 days count only half
        age_days = (timezone.now() - self.user.date_joined).days
        if age_days < 3:
            weight = weight / 2
        return weight

    def get_report_history(self):
        return self.user.food_reports.all().order_by('-created_at')




    def __str__(self):
        return f"{self.user.username} ({self.role})"


# a profile is created automatically whenever a new User is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)



class Vendor(models.Model):
    shop_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    area = models.CharField(max_length=100)
    risk_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


    def calculate_risk_score(self):
        # only reports that verifiers confirmed count (pending reports add nothing).
        # severity points x weight of the reporter, x5, maximum 100
        points = {'low': 1, 'medium': 2, 'high': 4, 'critical': 6}
        total = 0
        for r in self.foodreport_set.filter(status__in=['verified', 'resolved']):
            total += points[r.severity] * r.reporter.userprofile.get_weight()
        self.risk_score = min(100, round(total * 5, 1))
        self.save()
        return self.risk_score

    def check_alert(self):
        # create an area alert when the risk score reaches 40,
        # but not while a "possible coordinated attack" flag is open for this vendor
        from enforcement_app.models import AreaAlert
        from verification_app.models import FraudFlag, SPIKE_REASON
        under_attack = FraudFlag.objects.filter(
            report__vendor=self, status='open', reason__startswith=SPIKE_REASON).exists()
        if self.risk_score >= 40 and not under_attack:
            already = AreaAlert.objects.filter(vendor=self, is_active=True).exists()
            # after an alert was closed, a new one starts only if the risk is higher than it was then
            last = AreaAlert.objects.filter(vendor=self).order_by('-created_at').first()
            risen = last is None or self.risk_score > last.risk_score_at_trigger
            if not already and risen:
                AreaAlert.objects.create(
                    vendor=self, area=self.area, risk_score_at_trigger=self.risk_score)
                return True
        return False

    def __str__(self):
        return f"{self.shop_name} - {self.area}"