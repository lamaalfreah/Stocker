from django.db import models

# Create your models here.
from django.utils import timezone
from datetime import date

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self): return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    logo = models.ImageField(upload_to='suppliers/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    def __str__(self): return self.name

class Product(models.Model):
    name = models.CharField(max_length=150)         
    strength = models.CharField(max_length=50, blank=True)  # 500mg, 5mg/ml...
    form = models.CharField(max_length=50, blank=True)      # Tablet, Syrup...
    barcode = models.CharField(max_length=64, blank=True, null=True, unique=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    suppliers = models.ManyToManyField(Supplier, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)

    batch_no = models.CharField(max_length=64, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self): return f"{self.name} {self.strength}".strip()

    def is_low_stock(self): return self.quantity <= self.reorder_level
    def days_to_expiry(self):
        if not self.expiry_date: return None
        return (self.expiry_date - date.today()).days
    def is_near_expiry(self, days=30):
        d = self.days_to_expiry()
        return d is not None and d <= days
