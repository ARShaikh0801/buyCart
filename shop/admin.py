from django.contrib import admin

# Register your models here.
from .models import Product,Contact, Order, OrderUpdate,ProductImage,Rating,CartItem, Category, SubCategory


@admin.register(OrderUpdate)
class OrderUpdateAdmin(admin.ModelAdmin):
    list_display = ("order_id", "update_desc", "timestamp")
    readonly_fields = ("timestamp",)
    ordering = ('-timestamp',)
    search_fields = ("order_id",)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name","email","desc","timeStamp")
    readonly_fields=("name","email","phone","desc","timeStamp")
    list_filter=("timeStamp",)
    ordering = ('-timeStamp',)
    search_fields = ("name","email","phone")
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields=("order_id","items_json","amount","name","email","address","city","state","zip_code","phone_no","payment_status")
    list_display=("order_id","name","city","state","amount","payment_status")
    list_filter=("payment_status",)
    search_fields=("order_id","name","email","city","state","zip_code","phone_no")

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating", "created_at")
    readonly_fields = ("user", "product", "rating", "review", "created_at")

    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "product__product_name","product__id")
    ordering = ("-created_at",)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name", "category__name")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ("product_name", "category", "dealer", "discount","finalPrice","prodRating","ratingCount","pub_date","main_image")
    list_filter=("category","dealer","pub_date","prodRating")
    readonly_fields = ("prodRating", "ratingCount")
    search_fields=("id","product_name","category__name")
    ordering = ('-pub_date',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image")
    search_fields = ("product__product_name", "product__id")

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity", "selected_size")
    list_filter = ("user",)
    search_fields = ("user__username", "product__product_name")