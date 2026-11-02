from django.contrib import admin
from .models import Verification, FraudFlag

admin.site.register(Verification)
admin.site.register(FraudFlag)
