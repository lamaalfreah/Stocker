from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta

from inventory.models import Category, Supplier, Product

class Command(BaseCommand):
    help = "Seed demo data for the pharmacy inventory"

    @transaction.atomic
    def handle(self, *args, **options):
        # Users
        admin, _ = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@example.com', 'first_name': 'Admin', 'last_name': 'User'
        })
        if not admin.check_password('admin123'):
            admin.set_password('admin123')
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        employee, _ = User.objects.get_or_create(username='employee', defaults={
            'email': 'employee@example.com', 'first_name': 'Inventory', 'last_name': 'Clerk'
        })
        if not employee.check_password('employee123'):
            employee.set_password('employee123')
        employee.is_staff = False
        employee.is_superuser = False
        employee.save()

        self.stdout.write(self.style.SUCCESS("Users ready: admin/admin123, employee/employee123"))

        # Categories
        categories = [
            "Analgesics", "Antibiotics", "Antihistamines",
            "Cough & Cold", "Vitamins", "Devices"
        ]
        cat_map = {}
        for name in categories:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'description': name})
            cat_map[name] = cat
        self.stdout.write(self.style.SUCCESS("Categories ready."))

        # Suppliers
        sup_defs = [
            ("Medline", "sales@medline.com", "+1-555-1000", "https://medline.com", "USA"),
            ("PharmaOne", "hello@pharmaone.co", "+966-555-1111", "https://pharmaone.example", "Riyadh"),
            ("GulfMed", "info@gulfmed.co", "+971-555-2222", "https://gulfmed.example", "Dubai"),
            ("HealthPlus", "contact@healthplus.com", "+1-555-3333", "https://healthplus.example", "UK"),
        ]
        sup_map = {}
        for n, e, p, w, a in sup_defs:
            s, _ = Supplier.objects.get_or_create(name=n, defaults={
                'email': e, 'phone': p, 'website': w, 'address': a
            })
            sup_map[n] = s
        self.stdout.write(self.style.SUCCESS("Suppliers ready."))

        # Products (mix: some low stock, some near expiry, some normal)
        today = date.today()
        in_20d = today + timedelta(days=20)   # near expiry
        in_200d = today + timedelta(days=200)
        in_600d = today + timedelta(days=600)

        products = [
            # name, strength, form, barcode, category, price, qty, reorder, batch, expiry, suppliers
            ("Paracetamol", "500 mg", "Tablet", "1111111111111", "Analgesics", "5.00", 8, 10, "P-2025-01", in_600d, ["Medline", "PharmaOne"]),  # low stock
            ("Ibuprofen", "200 mg", "Tablet", "2222222222222", "Analgesics", "7.50", 60, 15, "I-2025-02", in_200d, ["Medline"]),
            ("Amoxicillin", "500 mg", "Capsule", "3333333333333", "Antibiotics", "18.00", 30, 10, "A-2025-03", in_20d, ["GulfMed"]),            # near expiry
            ("Cetirizine", "10 mg", "Tablet", "4444444444444", "Antihistamines", "9.00", 100, 20, "C-2025-04", in_600d, ["HealthPlus"]),
            ("Cough Syrup", "100 ml", "Syrup", "5555555555555", "Cough & Cold", "12.00", 5, 5, "CS-2025-05", in_20d, ["PharmaOne", "GulfMed"]),# low + near expiry
            ("Vitamin C", "1000 mg", "Tablet", "6666666666666", "Vitamins", "15.00", 80, 10, "VC-2025-06", in_600d, ["HealthPlus"]),
            ("Digital Thermometer", "", "Device", "7777777777777", "Devices", "25.00", 20, 5, "DT-2025-07", None, ["Medline"]),                 # non-perishable
        ]

        created = 0
        for (name, strength, form, barcode, cat_name, price, qty, reorder, batch, expiry, sups) in products:
            p, was_created = Product.objects.get_or_create(
                name=name, strength=strength, form=form,
                defaults={
                    'barcode': barcode, 'category': cat_map[cat_name],
                    'price': Decimal(price), 'quantity': qty,
                    'reorder_level': reorder, 'batch_no': batch,
                    'expiry_date': expiry
                }
            )
            if was_created:
                created += 1
            else:
                # update defaults in case they changed
                p.barcode = barcode
                p.category = cat_map[cat_name]
                p.price = Decimal(price)
                p.quantity = qty
                p.reorder_level = reorder
                p.batch_no = batch
                p.expiry_date = expiry
                p.save()

            # suppliers (M2M)
            p.suppliers.set([sup_map[s] for s in sups])

        self.stdout.write(self.style.SUCCESS(f"Products ready. Created/updated: {created}/{len(products)}"))

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
