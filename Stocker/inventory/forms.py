from django import forms
from datetime import date
from .models import Product, Category, Supplier


class DateInput(forms.DateInput):
    input_type = "date"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'strength', 'form', 'barcode', 'category', 'suppliers',
            'price', 'quantity', 'reorder_level', 'batch_no', 'expiry_date'
        ]
        labels = {
            'name': 'Product name',
            'strength': 'Strength',
            'form': 'Form',
            'barcode': 'Barcode',
            'category': 'Category',
            'suppliers': 'Suppliers',
            'price': 'Price',
            'quantity': 'Quantity',
            'reorder_level': 'Reorder level',
            'batch_no': 'Batch No.',
            'expiry_date': 'Expiry date',
        }
        help_texts = {
            'barcode': 'Optional.',
            'suppliers': 'Select one or more suppliers.',
            'expiry_date': 'Leave blank if this item has no expiry date.',
        }
        widgets = {
            'name':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Paracetamol'}),
            'strength':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 500 mg'}),
            'form':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tablet / Syrup'}),
            'barcode':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'EAN/UPC'}),
            'category':      forms.Select(attrs={'class': 'form-select'}),
            'suppliers':     forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'}),
            'price':         forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'placeholder': '0.00'}),
            'quantity':      forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '5'}),
            'batch_no':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. L2025-07'}),
            'expiry_date':   DateInput(attrs={'class': 'form-control'}),
        }

    # validations
    def clean_expiry_date(self):
        exp = self.cleaned_data.get('expiry_date')
        if exp and exp < date.today():
            raise forms.ValidationError("The expiration date cannot be in the past.")
        return exp

    def clean_price(self):
        v = self.cleaned_data.get('price')
        if v is not None and v < 0:
            raise forms.ValidationError("Price must be 0 or more.")
        return v

    def clean_quantity(self):
        v = self.cleaned_data.get('quantity')
        if v is not None and v < 0:
            raise forms.ValidationError("Quantity must be 0 or more.")
        return v

    def clean_reorder_level(self):
        v = self.cleaned_data.get('reorder_level')
        if v is not None and v < 0:
            raise forms.ValidationError("Reorder level must be 0 or more.")
        return v


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        labels = {'name': 'Name', 'description': 'Description'}
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Antibiotics'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'email', 'phone', 'logo', 'website', 'address']
        labels = {
            'name': 'Name',
            'email': 'Email',
            'phone': 'Phone',
            'logo': 'Logo',
            'website': 'Website',
            'address': 'Address',
        }
        widgets = {
            'name':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier name'}),
            'email':   forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'phone':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+966...'}),
            'logo':    forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Street, city...'}),
        }
