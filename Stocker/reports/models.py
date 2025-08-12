from django.db import models
from inventory.models import Product, Category, Supplier

# Create your models here.
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    suppliers = models.ManyToManyField(Supplier, blank=True, related_name='products')