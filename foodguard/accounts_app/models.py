from django.db import models

# Create your models here.
class Vendor(models.Model):
    shop_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    area = models.CharField(max_length=100)
    risk_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shop_name} - {self.area}"