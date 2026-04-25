from django import forms
from django.contrib.auth.models import User
from shop.models import Product, ProductImage, Category, SubCategory


class DealerRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username (lowercase & alphanumeric)',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com',
        })
    )
    business_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your business / brand name',
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a strong password',
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
        })
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if not username.isalnum():
            raise forms.ValidationError("Username should contain letters and numbers only.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class ProductForm(forms.ModelForm):
    stock_input = forms.CharField(
        label="Sizes & Stock",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. S:10, M:5 or just 50 if no sizes'})
    )
    is_sold_out = forms.BooleanField(
        label="Manually Mark as Sold Out",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    new_category = forms.CharField(
        label="Or Create New Category",
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter new category name'})
    )
    new_subcategory = forms.CharField(
        label="Or Create New Subcategory",
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter new subcategory name'})
    )

    class Meta:
        model = Product
        fields = [
            'product_name', 'category', 'subcategory',
            'price', 'discount',
            'desc', 'pub_date', 'main_image', 'is_sold_out'
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subcategory': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'MRP in ₹'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Discount %'}),
            'desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Product description'}),
            'pub_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'main_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['subcategory'].required = False
        if self.instance and self.instance.pk and self.instance.size_stocks:
            stocks = []
            for k, v in self.instance.size_stocks.items():
                if k == "Free Size":
                    stocks.append(str(v))
                else:
                    stocks.append(f"{k}:{v}")
            self.fields['stock_input'].initial = ", ".join(stocks)

    def clean_stock_input(self):
        val = self.cleaned_data.get('stock_input', '')
        size_stocks = {}
        available_sizes = []
        if val:
            parts = [p.strip() for p in val.split(',')]
            for p in parts:
                if ':' in p:
                    size, stock = p.split(':', 1)
                    size_stocks[size.strip().upper()] = int(stock.strip())
                    available_sizes.append(size.strip().upper())
                elif p.isdigit():
                    size_stocks["Free Size"] = int(p)
                    available_sizes.append("Free Size")
        return {
            'size_stocks': size_stocks,
            'available_sizes': ",".join(available_sizes)
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle new category creation
        new_cat_name = self.cleaned_data.get('new_category')
        if new_cat_name:
            category, created = Category.objects.get_or_create(name=new_cat_name.title())
            instance.category = category
        
        # Handle new subcategory creation
        new_subcat_name = self.cleaned_data.get('new_subcategory')
        if new_subcat_name:
            if instance.category:
                subcategory, created = SubCategory.objects.get_or_create(
                    category=instance.category, 
                    name=new_subcat_name.title()
                )
                instance.subcategory = subcategory
            else:
                # If no category is selected or created, we can't create a subcategory
                pass

        stock_data = self.cleaned_data.get('stock_input', {})
        if isinstance(stock_data, dict):
            instance.size_stocks = stock_data.get('size_stocks', {})
            instance.available_sizes = stock_data.get('available_sizes', '')
        if commit:
            instance.save()
        return instance


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
