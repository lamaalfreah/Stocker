from django.conf import settings
from django.core.mail import send_mail
from datetime import date, timedelta

def maybe_send_product_alert(product):
    """Send email if product is low stock or near expiry."""
    manager = getattr(settings, "MANAGER_EMAIL", None)
    if not manager:
        return

    msgs = []
    if product.quantity <= product.reorder_level:
        msgs.append(f"- Low stock: {product.name} (Qty: {product.quantity}, Reorder ≤ {product.reorder_level})")

    if product.expiry_date:
        soon = date.today() + timedelta(days=30)
        if product.expiry_date <= soon:
            msgs.append(f"- Near expiry: {product.name} (Expiry: {product.expiry_date})")

    if msgs:
        subject = "Inventory Alert"
        body = "The following items need attention:\n\n" + "\n".join(msgs)
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [manager], fail_silently=True)
