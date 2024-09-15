from django.urls import path, re_path
from . import views

urlpatterns = [
    path('add_collection/', views.add_daily_collection, name='add_collection'),
    path('collection_success/', views.collection_success, name='collection_success'),
    path('pdf/<int:bill_id>/', views.GeneratePdf.as_view(), name='generatepdf'),
]
