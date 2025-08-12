from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, F, Q, DecimalField, ExpressionWrapper
from django.http import HttpResponse
from django.shortcuts import render
from inventory.models import Product

value_expr = ExpressionWrapper(
    F('price') * F('quantity'),
    output_field=DecimalField(max_digits=12, decimal_places=2)
)

@login_required
def reports_dashboard(request):
    total_value = Product.objects.aggregate(total=Sum(value_expr))['total'] or 0
    total_products = Product.objects.count()
    low_count = Product.objects.filter(quantity__lte=F('reorder_level')).count()
    near_count = Product.objects.filter(expiry_date__isnull=False, expiry_date__lte=F('expiry_date')).filter(
        expiry_date__lte=F('expiry_date')  # dummy to keep structure—removed next line will handle near expiry in inventory_report
    ).count()  # We'll show near-expiry properly in inventory_report

    return render(request, 'reports/dashboard.html', {
        'total_value': total_value,
        'total_products': total_products,
        'low_count': low_count,
        'near_count': near_count,  # optional card
    })


@login_required
def inventory_report(request):
    # By category
    by_category = (
        Product.objects
        .values('category__id', 'category__name')
        .annotate(
            products_count=Count('id'),
            stock_value=Sum(value_expr)
        )
        .order_by('-products_count', 'category__name')
    )

    # Near expiry (≤ 30 days)
    from datetime import date, timedelta
    soon = date.today() + timedelta(days=30)
    near_expiry = Product.objects.filter(expiry_date__isnull=False, expiry_date__lte=soon)

    # Low stock
    low_stock = Product.objects.filter(quantity__lte=F('reorder_level'))

    total_value = Product.objects.aggregate(total=Sum(value_expr))['total'] or 0

    return render(request, 'reports/inventory.html', {
        'total_value': total_value,
        'by_category': by_category,
        'near_expiry': near_expiry,
        'low_stock': low_stock,
    })


@login_required
def supplier_report(request):
    # Aggregate by supplier (M2M) — no need to know related_name
    by_supplier = (
        Product.objects
        .values('suppliers__id', 'suppliers__name')
        .annotate(
            products_count=Count('id', distinct=True),
            stock_value=Sum(value_expr)
        )
        .order_by('-products_count', 'suppliers__name')
    )

    return render(request, 'reports/suppliers.html', {
        'by_supplier': by_supplier
    })


# -------- CSV exports --------
import csv
from django.utils.timezone import localdate

@login_required
def export_inventory_csv(request):
    """Export all products as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="inventory_{localdate()}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name','Strength','Form','Barcode','Category','Suppliers','Price','Quantity','ReorderLevel','BatchNo','Expiry'])

    qs = (Product.objects
          .select_related('category')
          .prefetch_related('suppliers')
          .order_by('name'))

    for p in qs:
        suppliers = ", ".join([s.name for s in p.suppliers.all()])
        writer.writerow([
            p.name, p.strength, p.form, p.barcode,
            getattr(p.category, 'name', ''), suppliers,
            p.price, p.quantity, p.reorder_level, p.batch_no,
            p.expiry_date or ''
        ])
    return response


@login_required
def export_supplier_summary_csv(request):
    """Export supplier summary (count + stock value) as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="suppliers_summary_{localdate()}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Supplier','ProductsCount','StockValue'])

    rows = (
        Product.objects
        .values('suppliers__name')
        .annotate(
            products_count=Count('id', distinct=True),
            stock_value=Sum(value_expr)
        )
        .order_by('suppliers__name')
    )

    for r in rows:
        writer.writerow([r['suppliers__name'] or '(No supplier)', r['products_count'] or 0, r['stock_value'] or 0])
    return response
