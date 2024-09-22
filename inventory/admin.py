from io import StringIO

from django.contrib import admin

from .forms import PurchaseOrderAdminForm, BillAdminForm
from .models import Company, Product, Dukandaar, Bill, DailyCollection, Item, PurchaseItem, PurchaseOrder, Area, CompanyPayment
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin import DateFieldListFilter

# Customizing the admin site titles (optional)
admin.site.site_header = "Neelkamal Admin"
admin.site.site_title = "Neelkamal Administration"
admin.site.index_title = "Manage Inventory and Bills"

# admin.site.unregister(Area)
# admin.site.unregister(Bill)
# admin.site.unregister(CompanyPayment)
# admin.site.unregister(Company)
# admin.site.unregister(DailyCollection)
# admin.site.unregister(Item)
# admin.site.unregister(Product)
# admin.site.unregister(PurchaseItem)
# admin.site.unregister(PurchaseOrder)
# admin.site.unregister(Dukandaar)

class PurchaseItemInLine(admin.TabularInline):
    model = PurchaseItem
    extra = 1

class ItemInLine(admin.TabularInline):
    model = Item
    extra = 1

class BillInline(admin.TabularInline):
    model = Bill
    extra = 1

class AreaAdmin(admin.ModelAdmin):
    list_display = ['area_name', 'city_name']

class DailyCollectionAdmin(admin.ModelAdmin):
    list_display = ['collection_time', 'dukandaar', 'amount_collected', 'pending_amount_as_of_today']
    list_filter = [
        ('collection_time', DateFieldListFilter),  # Filters by date, with day, month, and year options
        'dukandaar',
    ]
    autocomplete_fields = ['dukandaar']
    search_fields = ['dukandaar__name', 'collection_time']

    class Media:
        js = ('admin/js/admin_autofocus.js',)

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

    def has_add_permission(self, request, obj=None):
        return False

class ProductAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'stock_in_kg', 'stock_in_bora']

    def has_delete_permission(self, request, obj=None):
        # Only allow creating new Bill objects, not deleting existing ones
        return False

class BillAdmin(admin.ModelAdmin):
    inlines = [ItemInLine]
    form = BillAdminForm
    list_display = ['id', 'date', 'dukandaar', 'total_amount', 'paid', 'print_field']
    # Use autocomplete for the Dukandaar foreign key
    autocomplete_fields = ['dukandaar']
    list_filter = [
        ('date', DateFieldListFilter),
        'dukandaar',
        'paid'
    ]
    search_fields = ['dukandaar__name', 'date']

    class Media:
        js = ('admin/js/admin_autofocus.js',)

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
    form = PurchaseOrderAdminForm


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'loan_amount']


class CompanyPaymentAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount_paid']


class PurchaseItemAdmin(admin.ModelAdmin):
    fields = ['product', 'bora', 'kg', 'price_per_kg', 'amount']
    list_display = ['product', 'bora', 'kg', 'price_per_kg', 'amount']
    autocomplete_fields = ['product']

    def has_change_permission(self, request, obj=None):
        # Only allow creating new Bill objects, not changing existing ones
        return False

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(Bill, BillAdmin)
admin.site.register(Dukandaar, DukandaarAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(DailyCollection, DailyCollectionAdmin)
admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(PurchaseItem, PurchaseItemAdmin)
admin.site.register(CompanyPayment)
admin.site.register(Area, AreaAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Item, ItemAdmin)
