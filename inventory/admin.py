from io import StringIO

from django.contrib import admin
from .models import Company, Product, Dukandaar, Bill, DailyCollection, Item, PurchaseItem, PurchaseOrder, Area
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin import DateFieldListFilter

class PurchaseItemInLine(admin.TabularInline):
    model = PurchaseItem
    extra = 1

class ItemInLine(admin.TabularInline):
    model = Item
    extra = 1

class BillInline(admin.TabularInline):
    model = Bill
    extra = 1

class DailyCollectionAdmin(admin.ModelAdmin):
    list_display = ['collection_time', 'dukandaar', 'amount_collected']
    list_filter = [
        ('collection_time', DateFieldListFilter),  # Filters by date, with day, month, and year options
        'dukandaar',
    ]
    search_fields = ['dukandaar__name', 'collection_time']

class DukandaarAdmin(admin.ModelAdmin):
    inlines = [BillInline]
    list_display = ('name', 'contact_info', 'pending_amount')
    search_fields = ['name']

class ItemAdmin(admin.ModelAdmin):
    fields = ['product', 'kg', 'price_per_kg', 'amount']
    list_display = ['product', 'kg', 'price_per_kg', 'amount']
    autocomplete_fields = ['product']

    def has_change_permission(self, request, obj=None):
        # Only allow creating new Bill objects, not changing existing ones
        return False

class ProductAdmin(admin.ModelAdmin):
    search_fields = ['name']

class BillAdmin(admin.ModelAdmin):
    inlines = [ItemInLine]
    list_display = ['id', 'date', 'dukandaar', 'total_amount', 'paid', 'print_field']
    # Use autocomplete for the Dukandaar foreign key
    autocomplete_fields = ['dukandaar']
    list_filter = [
        ('date', DateFieldListFilter),  # Filters by date, with day, month, and year options
        'dukandaar',
        'paid'
    ]
    search_fields = ['dukandaar__name', 'date']

    def print_field(self, obj):
        print_url = reverse('generatepdf', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank"><button type="button">Print</button></a>',
            print_url
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        # Only allow creating new Bill objects, not changing existing ones
        return False


class PurchaseOrderAdmin(admin.ModelAdmin):
    inlines = [PurchaseItemInLine]

admin.site.register(Bill, BillAdmin)
admin.site.register(Company)
admin.site.register(Product, ProductAdmin)
admin.site.register(Dukandaar, DukandaarAdmin)
admin.site.register(DailyCollection, DailyCollectionAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(PurchaseItem)
admin.site.register(Area)