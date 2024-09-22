from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DailyCollectionForm
from django.views.generic import View
from django.shortcuts import get_object_or_404
from .utils import *
from django.http import HttpResponseForbidden

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

# Custom decorator to check if the user is a superuser
def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have permission to access this page.")
    return _wrapped_view

@login_required
@superuser_required
def analytics_view(request):
    context = {}
    context['sales'] = get_sales_count_comparison()
    context['revenue'] = get_monthly_revenue_comparison()
    context['customer'] = get_annual_customer_count_and_trend()
    context['todaysaleslist'] = get_todays_sales_list()
    context['topsellinglist'] = get_top_20_products_by_revenue()

    sales_data = get_last_15_days_sales_data()

    # Pass the data as context to the template
    context['sale_array'] = sales_data['sale_array']
    context['revenue_array'] = sales_data['revenue_array']
    context['customer_array'] = sales_data['customer_array']
    context['time_array'] = sales_data['time_array']

    spider_data = get_purchase_sell_data_for_chart()
    context['indicators'] = spider_data['indicators']
    context['purchase_values'] = spider_data['purchase_values']
    context['sell_values'] = spider_data['sell_values']

    context['products_sold'] = get_sold_products_last_month()

    context['user'] = request.user
    print((request.user))
    return render(request, 'analytics.html', context=context)


def index_page(request):
    context = {}
    return render(request, 'index.html', context=context)