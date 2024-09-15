from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse
from django.contrib.admin import SimpleListFilter
from datetime import datetime, timedelta


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
