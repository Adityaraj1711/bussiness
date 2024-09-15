from django import forms
from .models import DailyCollection

class DailyCollectionForm(forms.ModelForm):
    class Meta:
        model = DailyCollection
        fields = ['amount_collected', 'dukandaar']
