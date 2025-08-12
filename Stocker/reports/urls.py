from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),      # /reports/
    path('inventory/', views.inventory_report, name='inventory_report'),
    path('suppliers/', views.supplier_report, name='supplier_report'),

    # Exports (CSV)
    path('export/inventory.csv', views.export_inventory_csv, name='export_inventory_csv'),
    path('export/suppliers.csv', views.export_supplier_summary_csv, name='export_supplier_summary_csv'),
    ]



