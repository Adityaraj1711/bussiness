from django import forms
from .models import DailyCollection, PurchaseOrder, Company, Bill, Dukandaar

class DailyCollectionForm(forms.ModelForm):
    class Meta:
        model = DailyCollection
        fields = ['amount_collected', 'dukandaar']

class BillAdminForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BillAdminForm, self).__init__(*args, **kwargs)

class PurchaseOrderAdminForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PurchaseOrderAdminForm, self).__init__(*args, **kwargs)

        # Check if there's only one Dukandaar
        company = Company.objects.all()
        if len(company) == 1:
            # Auto-select the only available Dukandaar
            self.fields['company'].initial = company.first()
