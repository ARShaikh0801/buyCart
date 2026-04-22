import os
import django
from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buyCart.settings')
django.setup()

from shop.models import Product
from blog.models import Blogpost

def populate():
    print("Starting database population...")

    # Categories and items
    categories = {
        "Electronics": [
            {"name": "AeroPods Pro", "price": 12999, "discount": 10, "desc": "Next-generation wireless earbuds with active noise cancellation and spatial audio.", "sizes": "Standard"},
            {"name": "Quantum Watch Series 5", "price": 24999, "discount": 15, "desc": "A premium smartwatch featuring an OLED always-on display and advanced health tracking.", "sizes": "40mm, 44mm"},
            {"name": "Swift Click Mechanical Keyboard", "price": 8499, "discount": 20, "desc": "RGB mechanical keyboard with tactile blue switches for the ultimate typing experience.", "sizes": "Full, TKL"},
            {"name": "UltraDrive 1TB SSD", "price": 7999, "discount": 5, "desc": "High-speed portable SSD with USB 3.2 Gen 2 support. Durable and compact.", "sizes": "1TB, 2TB"},
            {"name": "GamerX Pro Mouse", "price": 3499, "discount": 12, "desc": "Ergonomic gaming mouse with 16,000 DPI and customizable macro buttons.", "sizes": "Default"}
        ],
        "Fashion": [
            {"name": "Classic Oxford Shirt", "price": 2499, "discount": 30, "desc": "Premium 100% cotton Oxford shirt. Perfect for formal and casual occasions.", "sizes": "S, M, L, XL"},
            {"name": "Heritage Leather Wallet", "price": 1499, "discount": 10, "desc": "Handcrafted genuine leather wallet with RFID protection and multiple card slots.", "sizes": "Standard"},
            {"name": "Velocity Sports Shoes", "price": 5999, "discount": 25, "desc": "Lightweight running shoes with responsive cushioning and breathable mesh.", "sizes": "7, 8, 9, 10, 11"},
            {"name": "Urban Denim Jacket", "price": 4499, "discount": 20, "desc": "Iconic denim jacket with a modern slim-fit cut and vintage wash finish.", "sizes": "M, L, XL"},
            {"name": "Aviator Polarized Glasses", "price": 2999, "discount": 15, "desc": "Classic aviator sunglasses with polarized lenses for superior UV protection.", "sizes": "One Size"}
        ],
        "Home Decor": [
            {"name": "Ceramic Zen Vase", "price": 1999, "discount": 5, "desc": "Minimalist handcrafted ceramic vase. Adds a touch of elegance to any room.", "sizes": "Small, Medium, Large"},
            {"name": "Lumina Touch Lamp", "price": 3499, "discount": 10, "desc": "Modern bedside lamp with 3-level touch brightness control and USB charging port.", "sizes": "Standard"},
            {"name": "Aroma Bliss Candle Set", "price": 1299, "discount": 0, "desc": "A set of 3 luxury scented candles (Lavender, Sandalwood, and Sea Salt).", "sizes": "Set of 3"},
            {"name": "Nordic Minimalist Clock", "price": 2499, "discount": 15, "desc": "Sleek wall clock with a silent movement mechanism and wooden accents.", "sizes": "Standard"},
            {"name": "CloudNine Throw Blanket", "price": 3999, "discount": 20, "desc": "Ultra-soft faux fur throw blanket for cozy nights. Machine washable.", "sizes": "Standard, Queen"}
        ]
    }

    # Image mapping
    image_map = {
        "Electronics": "shop/images/pexels-sparkphotopro-buycart.jpg",
        "Fashion": "shop/images/pexels-sparkphotopro-buycart.jpg",
        "Home Decor": "shop/images/pexels-sparkphotopro-buycart.jpg"
    }

    # Add Products
    for cat_name, items in categories.items():
        print(f"Adding category: {cat_name}")
        for item in items:
            p, created = Product.objects.get_or_create(
                product_name=item['name'],
                defaults={
                    'category': cat_name,
                    'price': item['price'],
                    'discount': item['discount'],
                    'desc': item['desc'],
                    'available_sizes': item['sizes'],
                    'pub_date': date.today(),
                    'main_image': image_map[cat_name]
                }
            )
            if created:
                print(f"  - Created Product: {item['name']}")
            else:
                print(f"  - Product already exists: {item['name']}")

    # Add Blogpost
    print("Adding Blogpost...")
    blog_title = "Unveiling Our Modern Collection: New Arrivals in Store!"
    blog_desc = """
    We are thrilled to announce the arrival of our latest collection at buyCart! 
    Whether you're looking to upgrade your tech, refresh your wardrobe, or give your home a makeover, we have something special for you.
    
    Our Electronics section now features the AeroPods Pro and the Quantum Watch Series 5—the pinnacle of wearable technology. 
    In Fashion, don't miss our handcrafted Heritage Leather Wallets and the versatile Classic Oxford Shirts.
    Finally, our Home Decor range has been expanded with minimalist Nordic Clocks and the ultra-soft CloudNine Throw Blankets.
    
    Check out the new arrivals today and enjoy exclusive launch discounts!
    """
    
    b, created = Blogpost.objects.get_or_create(
        title=blog_title,
        defaults={
            'description': blog_desc,
            'author': "BuyCart Team",
            'thumbnail': "blog/images/blog_hero.png"
        }
    )
    if created:
        print(f"  - Created Blogpost: {blog_title}")
    else:
        print(f"  - Blogpost already exists: {blog_title}")

    print("Population complete!")

if __name__ == "__main__":
    populate()
