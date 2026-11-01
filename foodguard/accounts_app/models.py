from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    def __str__(self):
        return f"{self.shop_name} - {self.area}"