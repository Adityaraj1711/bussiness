from django.urls import path, re_path
from . import views

urlpatterns = [
    path('add_collection/', views.add_daily_collection, name='add_collection'),
    path('collection_success/', views.collection_success, name='collection_success'),
    path('pdf/<int:bill_id>/', views.GeneratePdf.as_view(), name='generatepdf'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('', views.index_page, name='index'),
    path('admin/', views.redirect_to_admin, name='admin'),
    path('get_unpaid_bills/', views.get_unpaid_bills, name='get_unpaid_bills'),
]
