from django import forms
from .models import Investigation, ResolutionProof


class InvestigationForm(forms.ModelForm):
    class Meta:
        model = Investigation
        fields = ['status', 'priority', 'action_taken']


class ResolutionProofForm(forms.ModelForm):
    class Meta:
        model = ResolutionProof
        fields = ['proof_file', 'notes']
