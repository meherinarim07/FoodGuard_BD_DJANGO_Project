from django import forms
from .models import Verification


class VerificationForm(forms.ModelForm):
    class Meta:
        model = Verification
        fields = ['verdict', 'confidence', 'evidence_quality', 'comment']