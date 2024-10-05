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

class DailyCollectionForm(forms.ModelForm):
    class Meta:
        model = DailyCollection
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DailyCollectionForm, self).__init__(*args, **kwargs)
        # Initially, no bill is available, this will be populated based on the selected dukandaar
        self.fields['bill'].queryset = Bill.objects.none()

        if 'dukandaar' in self.data:
            try:
                dukandaar_id = int(self.data.get('dukandaar'))
                self.fields['bill'].queryset = Bill.objects.filter(dukandaar_id=dukandaar_id, paid=False)
            except (ValueError, TypeError):
                pass  # Invalid input; ignore and leave bill queryset empty
        elif self.instance.pk:
            self.fields['bill'].queryset = Bill.objects.filter(dukandaar=self.instance.dukandaar, paid=False)
