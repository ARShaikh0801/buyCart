from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.dealer_register, name='dealer_register'),
    path('login/', views.dealer_login, name='dealer_login'),
    path('logout/', views.dealer_logout, name='dealer_logout'),

    # Dashboard
    path('dashboard/', views.dealer_dashboard, name='dealer_dashboard'),

    # Product CRUD
    path('products/', views.dealer_products, name='dealer_products'),
    path('products/add/', views.dealer_product_add, name='dealer_product_add'),
    path('products/<int:product_id>/edit/', views.dealer_product_edit, name='dealer_product_edit'),
    path('products/<int:product_id>/delete/', views.dealer_product_delete, name='dealer_product_delete'),
]
