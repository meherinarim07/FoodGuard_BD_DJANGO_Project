from django import forms
from .models import FoodReport, Evidence, AwarenessPost


class FoodReportForm(forms.ModelForm):
    class Meta:
        model = FoodReport
        fields = ['vendor', 'food_item', 'description', 'severity']


class EvidenceForm(forms.ModelForm):
    class Meta:
        model = Evidence
        fields = ['image', 'caption']


class AwarenessPostForm(forms.ModelForm):
    class Meta:
        model = AwarenessPost
        fields = ['title', 'category', 'content', 'image']