from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse
from django.contrib.admin import SimpleListFilter
from datetime import date
from django.db.models import F
from datetime import timedelta, datetime
from django.db.models import Sum
from .models import Bill, Item, Dukandaar, PurchaseItem

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), dest=result, encoding="utf-8")
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors')

class DateRangeFilter(SimpleListFilter):
    title = 'collection date range'
    parameter_name = 'collection_date_range'

    def lookups(self, request, model_admin):
        return [
            ('last_30_days', 'Last 30 Days'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('this_year', 'This Year'),
        ]

    def queryset(self, request, queryset):
        today = datetime.now().date()
        if self.value() == 'last_30_days':
            start_date = today - timedelta(days=30)
            return queryset.filter(collection_time__range=[start_date, today])
        elif self.value() == 'this_month':
            start_date = today.replace(day=1)
            end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            return queryset.filter(collection_time__range=[start_date, end_date])
        elif self.value() == 'last_month':
            first_day_of_this_month = today.replace(day=1)
            last_month = first_day_of_this_month - timedelta(days=1)
            start_date = last_month.replace(day=1)
            end_date = last_month
            return queryset.filter(collection_time__range=[start_date, end_date])
        elif self.value() == 'this_year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
            return queryset.filter(collection_time__range=[start_date, end_date])
        return queryset

# 1. Fetch today's bill count and percentage increase or decrease compared to yesterday
def get_sales_count_comparison():
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Today's sales count
    todays_sales_count = Bill.objects.filter(date=today).count()

    # Yesterday's sales count
    yesterdays_sales_count = Bill.objects.filter(date=yesterday).count()

    # Calculate percentage increase or decrease
    if yesterdays_sales_count > 0:
        percentage_change = ((todays_sales_count - yesterdays_sales_count) / yesterdays_sales_count) * 100
    else:
        percentage_change = 100 if todays_sales_count > 0 else 0
    if percentage_change >= 0:
        return {
            "count": todays_sales_count,
            "increase": 1,
            "incrementPerc": percentage_change
        }
    else:
        return {
            "count": todays_sales_count,
            "decreasePerc": percentage_change,
            "increase": 0,
        }

# 2. Fetch total revenue of this month and percentage change compared to last month
def get_monthly_revenue_comparison():
    today = date.today()
    first_day_of_this_month = today.replace(day=1)
    first_day_of_last_month = (first_day_of_this_month - timedelta(days=1)).replace(day=1)

    # This month's revenue (sum of item amounts)
    this_month_revenue = Item.objects.filter(bill__date__gte=first_day_of_this_month).aggregate(
        total_revenue=Sum('amount')
    )['total_revenue'] or 0

    # Last month's revenue (sum of item amounts)
    last_month_revenue = Item.objects.filter(bill__date__gte=first_day_of_last_month,
                                             bill__date__lt=first_day_of_this_month).aggregate(
        total_revenue=Sum('amount')
    )['total_revenue'] or 0

    # Calculate percentage change
    if last_month_revenue > 0:
        percentage_change = ((this_month_revenue - last_month_revenue) / last_month_revenue) * 100
    else:
        percentage_change = 100 if this_month_revenue > 0 else 0
    if percentage_change >= 0:
        return {
            "month": this_month_revenue,
            "increasePerc": percentage_change,
            "increase": 1,
        }
    else:
        return {
            "month": this_month_revenue,
            "decreasePerc": percentage_change,
            "increase": 0,
        }


# 3. Fetch today's sales list
def get_todays_sales_list():
    today = date.today()
    yesterday = today - timedelta(1)
    todays_sales = Bill.objects.filter(date__in=[today, yesterday]).select_related('dukandaar').values(
        'id', 'dukandaar__name', 'total_amount', 'paid'
    )

    sales_list = [{
        'billid': sale['id'],
        'dukandaar': sale['dukandaar__name'],
        'amount': sale['total_amount'],
        'paid': sale['paid']
    } for sale in todays_sales]

    return sales_list


def get_top_20_products_by_revenue():
    today = date.today()
    first_day_of_this_month = today.replace(day=1)

    # Fetch products with total revenue generated in the current month, grouped by product id
    top_revenue_products = Item.objects.filter(bill__date__gte=first_day_of_this_month).values(
        'product__id', 'product__name', 'product__stock_in_kg'
    ).annotate(
        total_revenue=Sum('amount'),
        total_kgs_sold=Sum('kg') + Sum(F('bora') * F('product__one_bora_in_kg'))
    ).order_by('-total_revenue')[:20]

    # Construct the list of top-selling products by revenue
    product_list = [{
        'product_id': product['product__id'],
        'name': product['product__name'],
        'kgsold': product['total_kgs_sold'],
        'revenuegenerated': product['total_revenue'],
        'currentstock': product['product__stock_in_kg']
    } for product in top_revenue_products]

    return product_list

def get_annual_customer_count_and_trend():
    # Get the current year and previous year
    current_year = date.today().year
    previous_year = current_year - 1

    # Count customers who made bills in the current year
    current_year_customer_count = Dukandaar.objects.filter(
        bill__date__year=current_year
    ).distinct().count()

    # Count customers who made bills in the previous year
    previous_year_customer_count = Dukandaar.objects.filter(
        bill__date__year=previous_year
    ).distinct().count()

    # Calculate percentage increase or decrease
    if previous_year_customer_count == 0:
        # To avoid division by zero, we assume 100% increase if there were no customers last year
        percentage_change = 100 if current_year_customer_count > 0 else 0
    else:
        percentage_change = ((current_year_customer_count - previous_year_customer_count) / previous_year_customer_count) * 100

    # Create a result dictionary with the customer counts and the percentage change
    if percentage_change >= 0:
        return {
            'count': current_year_customer_count,
            'increase': 1,
            'increasePerc': percentage_change
        }
    else:
        return {
            'count': current_year_customer_count,
            'increase': 0,
            'decreasePerc': percentage_change
        }

def get_last_15_days_sales_data():
    # Initialize arrays
    sale_array = []
    revenue_array = []
    customer_array = []
    time_array = []

    # Get the current date and the start date (15 days ago)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=14)

    # Loop through each day in the last 15 days
    for i in range(30):
        current_date = start_date + timedelta(days=i)
        # Total revenue generated in thousands for the day
        total_revenue = Item.objects.filter(bill__date=current_date).aggregate(revenue=Sum('amount'))['revenue'] or 0
        if total_revenue == 0:
            continue
        revenue_array.append(int(total_revenue) / 1000)  # Convert to thousands

        # Bill count (sales) for the day
        bill_count = Bill.objects.filter(date=current_date).count()
        sale_array.append(bill_count)

        # Customer count (unique customers who had bills) for the day
        customer_count = Dukandaar.objects.filter(bill__date=current_date).distinct().count()
        customer_array.append(customer_count)

        # Time array (in the required format)
        time_string = current_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        time_array.append(time_string)

    # Return the result as a dictionary
    return {
        'sale_array': sale_array,
        'revenue_array': revenue_array,
        'customer_array': customer_array,
        'time_array': time_array
    }


def get_purchase_sell_data_for_chart():
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Get the total purchase value for each product bought this month
    purchases = (PurchaseItem.objects
                 .filter(purchase_order__date__month=current_month, purchase_order__date__year=current_year)
                 .values('product__name')
                 .annotate(total_purchase_value=Sum('amount')))

    # Get the total sell value for each product sold this month
    sells = (Item.objects
             .filter(bill__date__month=current_month, bill__date__year=current_year)
             .values('product__name')
             .annotate(total_sell_value=Sum('amount')))

    # Prepare the dynamic product list with 300000 as the maximum for each indicator
    indicators = []
    purchase_values = []
    sell_values = []

    # Get unique product names from purchases and sells
    product_names = set([p['product__name'] for p in purchases] + [s['product__name'] for s in sells])

    # Loop through each product and prepare indicators and values
    for product_name in product_names:
        # Find the corresponding purchase and sell values (default to 0 if not present)
        purchase_value = next((int(p['total_purchase_value']) for p in purchases if p['product__name'] == product_name), 0)
        sell_value = next((int(s['total_sell_value']) for s in sells if s['product__name'] == product_name), 0)

        # Append the indicator with max value 100000
        indicators.append({'name': product_name, 'max': 100000})

        # Append the purchase and sell values
        purchase_values.append(purchase_value)
        sell_values.append(sell_value)

    # Return the radar chart data
    return {
        'indicators': indicators,
        'purchase_values': purchase_values,
        'sell_values': sell_values
    }

def get_sold_products_last_month():
    # Calculate the date range for the last month
    today = datetime.now()
    last_30_date = today - timedelta(days=30)

    # Query to get the unique products sold in the last month
    sold_products = (Item.objects
                     .filter(bill__date__range=[last_30_date, today])  # Filter bills within the last month
                     .values('product__name')  # Group by product name
                     .annotate(total_kgs_sold=Sum(F('kg') + F('bora') * F('product__one_bora_in_kg'))))

    # Convert the QuerySet to a list of dictionaries
    result = [{'name': item['product__name'], 'value': float(item['total_kgs_sold'])} for item in sold_products]

    return result
