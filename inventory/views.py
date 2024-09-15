from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DailyCollectionForm
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from django.views.generic import View
from django.shortcuts import get_object_or_404
from .models import Bill


@login_required
def add_daily_collection(request):
    if not request.user.is_staff:
        return redirect('admin:index')

    if request.method == 'POST':
        form = DailyCollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.staff = request.user
            collection.save()
            return redirect('collection_success')
    else:
        form = DailyCollectionForm()

    return render(request, 'inventory/daily_collection_form.html', {'form': form})

@login_required
def collection_success(request):
    return render(request, 'inventory/collection_success.html')

class GeneratePdf(View):
    def get(self, request, bill_id, *args, **kwargs):
        # Retrieve the Bill object
        bill = get_object_or_404(Bill, pk=bill_id)

        # Define the context as a dictionary
        context = {
            'bill': bill
        }

        # Render the template with context
        template = get_template('bill_template.html')
        html = template.render(context)

        # Create a response object for the PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="bill_{}.pdf"'.format(bill.id)

        # Generate the PDF
        pisa_status = pisa.CreatePDF(html, dest=response)

        # If an error occurs during PDF generation
        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500)

        return response