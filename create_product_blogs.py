import os
import django
from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buyCart.settings')
django.setup()

from shop.models import Product
from blog.models import Blogpost

def generate_product_blogs():
    print("Starting product blog generation...")
    products = Product.objects.all()
    
    if not products.exists():
        print("No products found in the database.")
        return

    for product in products:
        # Check if blog post already exists for this product
        if Blogpost.objects.filter(product=product).exists():
            print(f"Blog post already exists for: {product.product_name}")
            continue

        title = f"Review: Why {product.product_name} is the Best Choice for You!"
        
        # Create a "proper" HTML description
        description = f"""
        <p>In today's fast-paced world, finding quality products that actually deliver on their promises can be a challenge. That's why we're so excited to feature the <strong>{product.product_name}</strong> in our latest product spotlight.</p>
        
        <h3>Premium Quality & Design</h3>
        <p>{product.desc}</p>
        
        <h3>Why We Love It</h3>
        <ul>
            <li><strong>Exceptional Performance:</strong> Designed for reliability and style.</li>
            <li><strong>Versatile Use:</strong> Perfect for any occasion or setting.</li>
            <li><strong>Unbeatable Value:</strong> Currently available at a special discount.</li>
        </ul>
        
        <p>Whether you're a long-time fan of {product.category.name if product.category else 'our collection'} or looking for your first piece, the {product.product_name} is a must-have addition. Don't miss out on the chance to own this premium item at an incredible price.</p>
        
        <blockquote>
            "The {product.product_name} isn't just a product; it's an experience. We've seen incredible feedback from our community about its durability and sleek design."
        </blockquote>
        
        <p>Scroll down to see the full details and grab yours today!</p>
        """

        Blogpost.objects.create(
            title=title,
            description=description,
            author="buyCart Editorial Team",
            thumbnail=product.main_image,
            product=product
        )
        print(f"Created blog post for: {product.product_name}")

    print("Generation complete!")

if __name__ == "__main__":
    generate_product_blogs()
