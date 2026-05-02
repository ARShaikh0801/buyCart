<h1 align="center">buyCart</h1>

<p align="center">
  <strong>A modern, feature-rich e-commerce platform built with Django.</strong>
</p>

## Overview

buyCart is a comprehensive e-commerce web application that bridges the gap between customers and dealers. It features a complete shopping experience with a dedicated dealer portal, allowing vendors to manage their inventory and engage with customers through product blogs.

### Key Features

- **Multi-Role System**: Distinct experiences for customers and dealers.
- **Dealer Dashboard**: A dedicated portal for dealers to track sales, manage inventory, and publish product-related blogs.
- **Secure Payments**: Fully integrated with Stripe for seamless, secure checkout experiences.
- **Blogging Platform**: Dealers can create rich-text blog posts about their products using the integrated Quill Editor to drive engagement.
- **Responsive Design**: A carefully crafted, mobile-first UI built with modern CSS and Bootstrap 5.
- **Order Management**: Built-in cart functionality, checkout process, and order tracking system.
- **Product Reviews**: Customers can leave ratings and reviews on products.

## Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Bootstrap 5
- **Payments:** Stripe API
- **Database:** SQLite (Development)

## Gallery

Here is a glimpse into the buyCart platform:

### Customer Experience

<details>
<summary><b>Shop Home Page</b></summary>
<br>
<img src="Project%20ss/shop%20home%20page.png" alt="Shop Home Page" width="100%">
</details>

<details>
<summary><b>Mobile Responsive Design</b></summary>
<br>
<img src="Project%20ss/shop%20home%20page%20in%20mobile.png" alt="Shop Home Page in Mobile" width="400">
</details>

<details>
<summary><b>Product View Page</b></summary>
<br>
<img src="Project%20ss/product%20view%20page.png" alt="Product View Page" width="100%">
</details>

<details>
<summary><b>Blog Integration</b></summary>
<br>
<img src="Project%20ss/blog%20page.png" alt="Blog Page" width="100%">
</details>

<details>
<summary><b>Order Tracker</b></summary>
<br>
<img src="Project%20ss/tracker%20page.png" alt="Tracker Page" width="100%">
</details>

### Payment Flow

<details>
<summary><b>Stripe Checkout Integration</b></summary>
<br>
<img src="Project%20ss/stripe%20payment%20gateway%20integartion%20for%20card%20payments.png" alt="Stripe Payment" width="100%">
</details>

### Dealer Portal

<details>
<summary><b>Dealer Dashboard</b></summary>
<br>
<img src="Project%20ss/dealer%20dashboard%20page.jpeg" alt="Dealer Dashboard" width="100%">
</details>

<details>
<summary><b>Product Management</b></summary>
<br>
<img src="Project%20ss/my%20products%20page%20for%20dealer.jpeg" alt="Dealer Products Page" width="100%">
</details>

<details>
<summary><b>Blog Management</b></summary>
<br>
<img src="Project%20ss/my%20blogs%20page.png" alt="Dealer Blogs Page" width="100%">
</details>

*(More screenshots are available in the `Project ss` directory)*

## Demo Video

https://github.com/user-attachments/assets/1b4b4c66-49c0-45fd-a2d3-17d0c8f6c9a8

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/ARShaikh0801/buyCart.git 
   cd buyCart
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the project root and add your necessary environment variables (e.g., for Stripe payments):
   ```env
   STRIPE_PUBLIC_KEY=your_stripe_public_key
   STRIPE_SECRET_KEY=your_stripe_secret_key
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```
   *The application will be available at `http://127.0.0.1:8000/`*

## Author

**Shaikh Abdulrauf A.**
