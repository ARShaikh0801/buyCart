import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.forms import modelformset_factory

from django.db.models import Q
from shop.models import Product, ProductImage, Order, Category
from .models import DealerProfile
from .forms import DealerRegistrationForm, ProductForm, ProductImageForm
from .mixins import dealer_required


# ── Authentication ───────────────────────────────────────────────

def dealer_register(request):
    """Separate registration flow for dealers."""
    if request.user.is_authenticated and hasattr(request.user, 'dealerprofile'):
        return redirect('dealer_dashboard')

    if request.method == 'POST':
        form = DealerRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            DealerProfile.objects.create(
                user=user,
                business_name=form.cleaned_data['business_name'],
                phone=form.cleaned_data.get('phone', ''),
            )
            login(request, user)
            messages.success(request, "Dealer account created successfully! Welcome to your dashboard.")
            return redirect('dealer_dashboard')
    else:
        form = DealerRegistrationForm()

    return render(request, 'dealer/register.html', {'form': form})


def dealer_login(request):
    """Separate login flow for dealers."""
    if request.user.is_authenticated and hasattr(request.user, 'dealerprofile'):
        return redirect('dealer_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)

        if user is not None:
            if hasattr(user, 'dealerprofile') and user.dealerprofile.is_dealer:
                login(request, user)
                messages.success(request, "Welcome back!")
                return redirect('dealer_dashboard')
            else:
                messages.error(request, "This account is not registered as a dealer.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'dealer/login.html')


def dealer_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('dealer_login')


# ── Dashboard & Stats ────────────────────────────────────────────

@dealer_required
def dealer_dashboard(request):
    """Stats overview — total products, units sold, revenue using ORM + parsed JSON."""
    dealer_products = Product.objects.filter(dealer=request.user)
    total_products = dealer_products.count()

    # Build a set of this dealer's product IDs for fast lookup
    dealer_product_ids = set(dealer_products.values_list('id', flat=True))

    # Parse orders to compute units sold & revenue
    orders = Order.objects.exclude(payment_status__in=['', 'pending'])
    total_sold = 0
    total_revenue = 0.0

    for order in orders:
        try:
            items = json.loads(order.items_json)
        except (json.JSONDecodeError, TypeError):
            continue
        for key, val in items.items():
            try:
                pid = int(key.replace('pr', ''))
            except (ValueError, AttributeError):
                continue
            if pid in dealer_product_ids:
                qty = int(val[0])
                price = float(val[2])
                total_sold += qty
                total_revenue += qty * price

    context = {
        'total_products': total_products,
        'total_sold': total_sold,
        'total_revenue': total_revenue,
        'recent_products': dealer_products.order_by('-pub_date')[:5],
    }
    return render(request, 'dealer/dashboard.html', context)


# ── Product CRUD ─────────────────────────────────────────────────

@dealer_required
def dealer_products(request):
    """List all products owned by the current dealer with search and filters."""
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    status = request.GET.get('status', '')

    products = Product.objects.filter(dealer=request.user)

    if query:
        products = products.filter(
            Q(product_name__icontains=query) | 
            Q(desc__icontains=query) |
            Q(subcategory__name__icontains=query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    if status == 'in_stock':
        products = [p for p in products if not p.check_sold_out]
    elif status == 'sold_out':
        products = [p for p in products if p.check_sold_out]

    if not isinstance(products, list):
        products = products.order_by('-pub_date')

    categories = Category.objects.filter(product__dealer=request.user).distinct()

    context = {
        'products': products,
        'categories': categories,
        'current_q': query,
        'current_cat': category_id,
        'current_status': status,
    }
    return render(request, 'dealer/product_list.html', context)


@dealer_required
def dealer_product_add(request):
    """Add a new product with optional extra images."""
    ImageFormSet = modelformset_factory(ProductImage, form=ProductImageForm, extra=3, can_delete=False)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ImageFormSet(request.POST, request.FILES, queryset=ProductImage.objects.none(), prefix='images')

        if form.is_valid() and formset.is_valid():
            product = form.save(commit=False)
            product.dealer = request.user
            product.save()

            for img_form in formset.cleaned_data:
                if img_form and img_form.get('image'):
                    ProductImage.objects.create(product=product, image=img_form['image'])

            messages.success(request, f'"{product.product_name}" has been added successfully!')
            return redirect('dealer_products')
    else:
        form = ProductForm()
        formset = ImageFormSet(queryset=ProductImage.objects.none(), prefix='images')

    return render(request, 'dealer/product_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Add New Product',
        'submit_text': 'Add Product',
    })


@dealer_required
def dealer_product_edit(request, product_id):
    """Edit an existing product (only if owned by current dealer)."""
    product = get_object_or_404(Product, id=product_id, dealer=request.user)
    ImageFormSet = modelformset_factory(ProductImage, form=ProductImageForm, extra=2, can_delete=True)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ImageFormSet(
            request.POST, request.FILES,
            queryset=ProductImage.objects.filter(product=product),
            prefix='images',
        )

        if form.is_valid() and formset.is_valid():
            form.save()

            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            for instance in instances:
                instance.product = product
                instance.save()

            messages.success(request, f'"{product.product_name}" updated successfully!')
            return redirect('dealer_products')
    else:
        form = ProductForm(instance=product)
        formset = ImageFormSet(
            queryset=ProductImage.objects.filter(product=product),
            prefix='images',
        )

    return render(request, 'dealer/product_form.html', {
        'form': form,
        'formset': formset,
        'title': f'Edit: {product.product_name}',
        'submit_text': 'Save Changes',
        'product': product,
    })


@dealer_required
def dealer_product_delete(request, product_id):
    """Delete a product (only if owned by current dealer)."""
    product = get_object_or_404(Product, id=product_id, dealer=request.user)

    if request.method == 'POST':
        name = product.product_name
        product.delete()
        messages.success(request, f'"{name}" has been deleted.')
        return redirect('dealer_products')

    return render(request, 'dealer/product_confirm_delete.html', {'product': product})
