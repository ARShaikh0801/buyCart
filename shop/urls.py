from django.urls import path
from . import views

urlpatterns = [
    path("", views.index,name="ShopHome"),
    path("about/", views.about,name="AboutUs"),
    path("contact/", views.contact,name="ContactUs"),
    path("tracker/", views.tracker,name="TrackingStatus"),
    path("search/", views.search,name="Search"),
    path("products/<int:myid>", views.productView,name="ProductView"),
    path("checkout/", views.checkout,name="Checkout"),
    path('signup/',views.handleSignup,name='handleSignup'),
    path('login/',views.handleLogin,name='handleLogin'),
    path('logout/',views.handleLogout,name='handleLogout'),
    path('gateway/',views.handlePayment,name='gateway'),
    path('rating/',views.rateProduct,name='rating'),
    path('filter/',views.filters,name='filters'),
    # Cart API endpoints
    path('api/cart/', views.api_get_cart, name='api_get_cart'),
    path('api/cart/update/', views.api_update_cart_item, name='api_update_cart_item'),
    path('api/cart/remove/', views.api_remove_cart_item, name='api_remove_cart_item'),
    path('api/cart/clear/', views.api_clear_cart, name='api_clear_cart'),
    # Stripe endpoints
    path('stripe/create-session/', views.create_stripe_session, name='create_stripe_session'),
    path('stripe/success/', views.stripe_success, name='stripe_success'),
    path('stripe/cancel/', views.stripe_cancel, name='stripe_cancel'),
]