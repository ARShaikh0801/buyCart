from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ('category', 'name')
        verbose_name_plural = "Sub Categories"

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Product(models.Model):
    product_name=models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    dealer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dealer_products')
    available_sizes = models.CharField(max_length=100,help_text="Enter sizes comma separated. Example: S,M,L or 6,7,8,9",default="")
    price=models.IntegerField(default=0,help_text="Enter MRP on Product")
    discount=models.IntegerField(default=0,help_text="Enter discount in percentage")
    finalPrice=models.IntegerField(default=0,editable=False)
    desc=models.CharField(max_length=100000)
    pub_date=models.DateField()
    main_image = models.ImageField(upload_to="shop/images")
    is_sold_out = models.BooleanField(default=False, help_text="Manually mark product as sold out")
    size_stocks = models.JSONField(default=dict, blank=True, null=True, help_text="Format: {'S': 10, 'M': 5}")
    prodRating = models.FloatField(default=0.0)
    ratingCount = models.IntegerField(default=0)
    
    @property
    def check_sold_out(self):
        if self.is_sold_out:
            return True
        if self.size_stocks:
            total_stock = sum(int(v) for v in self.size_stocks.values() if str(v).isdigit() or isinstance(v, int))
            if total_stock <= 0:
                return True
        return False
    
    def save(self, *args,**kwargs):
        if (not self.discount) or (self.discount==0):
            self.finalPrice=self.price
        elif self.price:
            self.finalPrice=self.price-int((self.price*self.discount/100))-1
        self.available_sizes = self.available_sizes.upper().replace(" ", "")
        super().save(*args,**kwargs)

    def __str__(self):
        return self.product_name
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="extra_images")
    image = models.ImageField(upload_to="shop/product_images")

    def __str__(self):
        return f"Image of {self.product.product_name}"

class Contact(models.Model):
    msg_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    email= models.CharField(max_length=50,default="")
    phone= models.CharField(max_length=13,default="")
    desc=models.CharField(max_length=2000,default="")
    timeStamp=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    order_id=models.AutoField(primary_key=True)
    items_json=models.CharField(max_length=5000)
    amount=models.FloatField(default=0.0)
    name=models.CharField(max_length=90)
    email=models.CharField(max_length=120)
    address=models.CharField(max_length=200)
    city=models.CharField(max_length=120)
    state=models.CharField(max_length=60)
    zip_code=models.CharField(max_length=6)
    phone_no=models.CharField(max_length=15)
    payment_status=models.CharField(max_length=25,default="")
class OrderUpdate(models.Model):
    update_id=models.AutoField(primary_key=True)
    order_id=models.IntegerField(default=0)
    update_desc=models.CharField(max_length=5000)
    timestamp=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order_id)+" : "+ self.update_desc
    
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    selected_size = models.CharField(max_length=20, blank=True, default='')

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name} x{self.quantity}"

