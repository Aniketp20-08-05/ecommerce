"""
seed_mock_data.py
=================
Run with:  python seed_mock_data.py
from the project root (same folder as manage.py).

Creates:
  • 2 Retailers  (retailer1 / retailer2)
  • 3 Consumers  (consumer1 / consumer2 / consumer3)
  • 6 Categories
  • 20 Products  (10 per retailer)
  • Cart items   for each consumer
  • 7 Orders     with various statuses
"""

import os
import sys
import django
from decimal import Decimal

# ── Bootstrap Django ──────────────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# ── Imports (after setup) ─────────────────────────────────────────────────────
from django.contrib.auth import get_user_model
from users.models import UserProfile
from catalog.models import Category, Product
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem

User = get_user_model()

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_or_create_user(username, email, password, role):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email}
    )
    if created:
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, role=role)
        print(f"  Created {role}: {username}")
    else:
        UserProfile.objects.get_or_create(user=user, defaults={"role": role})
        print(f"  Already exists, skipping: {username}")
    return user


def get_or_create_category(name, slug):
    cat, created = Category.objects.get_or_create(slug=slug, defaults={"name": name})
    if created:
        print(f"  Created category: {name}")
    return cat


# ─────────────────────────────────────────────────────────────────────────────
# 1. Users
# ─────────────────────────────────────────────────────────────────────────────

print("\n=== Creating Users ===")

retailer1 = get_or_create_user("retailer1", "retailer1@shop.com", "Retailer@123", "retailer")
retailer2 = get_or_create_user("retailer2", "retailer2@shop.com", "Retailer@123", "retailer")

consumer1 = get_or_create_user("consumer1", "consumer1@mail.com", "Consumer@123", "consumer")
consumer2 = get_or_create_user("consumer2", "consumer2@mail.com", "Consumer@123", "consumer")
consumer3 = get_or_create_user("consumer3", "consumer3@mail.com", "Consumer@123", "consumer")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Categories
# ─────────────────────────────────────────────────────────────────────────────

print("\n=== Creating Categories ===")

electronics   = get_or_create_category("Electronics",    "electronics")
clothing      = get_or_create_category("Clothing",       "clothing")
books         = get_or_create_category("Books",          "books")
home_kitchen  = get_or_create_category("Home & Kitchen", "home-kitchen")
sports        = get_or_create_category("Sports",         "sports")
beauty        = get_or_create_category("Beauty",         "beauty")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Products  (10 per retailer)
# ─────────────────────────────────────────────────────────────────────────────

print("\n=== Creating Products ===")

PRODUCTS_R1 = [
    ("Wireless Bluetooth Headphones",
     "Premium noise-cancelling over-ear headphones with 30-hour battery life.",
     2999.00, 50, electronics),
    ("Smart LED TV 43 inch",
     "4K UHD Android TV with built-in streaming apps and voice control.",
     32999.00, 20, electronics),
    ("Men's Running Shoes",
     "Lightweight breathable mesh shoes with cushioned sole for daily runs.",
     1799.00, 80, sports),
    ("Yoga Mat Anti-Slip",
     "6mm thick eco-friendly TPE yoga mat with alignment lines.",
     899.00, 120, sports),
    ("The Pragmatic Programmer",
     "Classic software engineering book by Andrew Hunt & David Thomas.",
     599.00, 40, books),
    ("Clean Code by Robert Martin",
     "A handbook of agile software craftsmanship.",
     549.00, 35, books),
    ("Non-stick Cookware Set 5pcs",
     "Granite-coated induction-friendly pots and pans set.",
     2199.00, 30, home_kitchen),
    ("Electric Kettle 1.5L",
     "Stainless steel kettle with auto shut-off and boil-dry protection.",
     799.00, 60, home_kitchen),
    ("Men's Formal Shirt",
     "100% cotton slim-fit formal shirt, wrinkle-resistant.",
     699.00, 100, clothing),
    ("Women's Kurti Floral Print",
     "Comfortable rayon floral-print kurti, available in multiple sizes.",
     449.00, 150, clothing),
]

PRODUCTS_R2 = [
    ("USB-C Fast Charger 65W",
     "GaN technology charger compatible with laptops, phones and tablets.",
     1499.00, 75, electronics),
    ("Mechanical Gaming Keyboard",
     "RGB backlit TKL keyboard with Cherry MX Red switches.",
     3499.00, 25, electronics),
    ("Men's Gym Track Pants",
     "Moisture-wicking polyester track pants with zip pockets.",
     599.00, 90, sports),
    ("Protein Shaker Bottle 700ml",
     "BPA-free shaker with mixing ball and measurement markings.",
     299.00, 200, sports),
    ("Atomic Habits by James Clear",
     "Tiny changes, remarkable results — a bestselling self-help book.",
     449.00, 60, books),
    ("Deep Work by Cal Newport",
     "Rules for focused success in a distracted world.",
     399.00, 45, books),
    ("Vitamin C Face Serum 30ml",
     "Brightening serum with 20% vitamin C, niacinamide and hyaluronic acid.",
     699.00, 80, beauty),
    ("Sunscreen SPF 50+ 100ml",
     "Lightweight matte finish sunscreen, water-resistant for 4 hours.",
     349.00, 110, beauty),
    ("Air Fryer 4.5L Digital",
     "1500W rapid air circulation fryer with 8 preset cooking programs.",
     4499.00, 18, home_kitchen),
    ("Women's Casual T-Shirt Pack of 3",
     "Soft cotton round-neck t-shirts in 3 contrasting colours.",
     799.00, 130, clothing),
]


def seed_products(retailer, product_list):
    created_products = []
    for name, desc, price, stock, cat in product_list:
        prod, created = Product.objects.get_or_create(
            name=name,
            retailer=retailer,
            defaults={
                "description": desc,
                "price": Decimal(str(price)),
                "stock": stock,
                "category": cat,
                "is_active": True,
            }
        )
        if created:
            print(f"  Created product: {name}")
        else:
            print(f"  Already exists: {name}")
        created_products.append(prod)
    return created_products


prods_r1 = seed_products(retailer1, PRODUCTS_R1)
prods_r2 = seed_products(retailer2, PRODUCTS_R2)
all_products = prods_r1 + prods_r2

# ─────────────────────────────────────────────────────────────────────────────
# 4. Cart items
# ─────────────────────────────────────────────────────────────────────────────

print("\n=== Adding Cart Items ===")

CART_DATA = {
    consumer1: [(all_products[0], 1), (all_products[6], 2)],
    consumer2: [(all_products[10], 1), (all_products[16], 3)],
    consumer3: [(all_products[4], 1), (all_products[12], 2), (all_products[18], 1)],
}

for consumer, items in CART_DATA.items():
    cart, _ = Cart.objects.get_or_create(user=consumer)
    for product, qty in items:
        _, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": qty}
        )
        if created:
            print(f"  Cart [{consumer.username}]: {product.name} x{qty}")
        else:
            print(f"  Already in cart: {consumer.username} -> {product.name}")

# ─────────────────────────────────────────────────────────────────────────────
# 5. Orders
# ─────────────────────────────────────────────────────────────────────────────

print("\n=== Creating Orders ===")

ORDER_DATA = [
    (
        consumer1, Order.Status.DELIVERED,
        [(all_products[1], 1), (all_products[7], 1)],
        {"ship_name": "Rahul Sharma", "ship_phone": "9876543210",
         "ship_address": "12 MG Road", "ship_city": "Bengaluru",
         "ship_state": "Karnataka", "ship_pincode": "560001"},
    ),
    (
        consumer1, Order.Status.SHIPPED,
        [(all_products[8], 2)],
        {"ship_name": "Rahul Sharma", "ship_phone": "9876543210",
         "ship_address": "12 MG Road", "ship_city": "Bengaluru",
         "ship_state": "Karnataka", "ship_pincode": "560001"},
    ),
    (
        consumer1, Order.Status.PLACED,
        [(all_products[5], 1)],
        {"ship_name": "Rahul Sharma", "ship_phone": "9876543210",
         "ship_address": "12 MG Road", "ship_city": "Bengaluru",
         "ship_state": "Karnataka", "ship_pincode": "560001"},
    ),
    (
        consumer2, Order.Status.PAID,
        [(all_products[11], 1), (all_products[13], 3)],
        {"ship_name": "Priya Mehta", "ship_phone": "9123456780",
         "ship_address": "45 Park Street", "ship_city": "Kolkata",
         "ship_state": "West Bengal", "ship_pincode": "700016"},
    ),
    (
        consumer2, Order.Status.CANCELLED,
        [(all_products[17], 2)],
        {"ship_name": "Priya Mehta", "ship_phone": "9123456780",
         "ship_address": "45 Park Street", "ship_city": "Kolkata",
         "ship_state": "West Bengal", "ship_pincode": "700016"},
    ),
    (
        consumer3, Order.Status.DELIVERED,
        [(all_products[14], 1), (all_products[15], 1)],
        {"ship_name": "Arjun Nair", "ship_phone": "9988776655",
         "ship_address": "7 Anna Salai", "ship_city": "Chennai",
         "ship_state": "Tamil Nadu", "ship_pincode": "600002"},
    ),
    (
        consumer3, Order.Status.PLACED,
        [(all_products[9], 3), (all_products[19], 2)],
        {"ship_name": "Arjun Nair", "ship_phone": "9988776655",
         "ship_address": "7 Anna Salai", "ship_city": "Chennai",
         "ship_state": "Tamil Nadu", "ship_pincode": "600002"},
    ),
]

for consumer, status, items, ship in ORDER_DATA:
    total = sum(p.price * qty for p, qty in items)

    if Order.objects.filter(user=consumer, total=total, status=status).exists():
        print(f"  Order already exists: {consumer.username} ({status})")
        continue

    order = Order.objects.create(
        user=consumer,
        status=status,
        total=total,
        **ship
    )
    for product, qty in items:
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=qty,
            unit_price=product.price
        )
    print(f"  Order [{consumer.username}] status={status} total=Rs.{total:.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 50)
print("  MOCK DATA SEEDING COMPLETE")
print("=" * 50)
print(f"  Retailers  : {User.objects.filter(profile__role='retailer').count()}")
print(f"  Consumers  : {User.objects.filter(profile__role='consumer').count()}")
print(f"  Categories : {Category.objects.count()}")
print(f"  Products   : {Product.objects.count()}")
print(f"  Carts      : {Cart.objects.count()}")
print(f"  Orders     : {Order.objects.count()}")
print("=" * 50)
print("\nLogin Credentials:")
print("  Retailers  -> retailer1 / Retailer@123")
print("             -> retailer2 / Retailer@123")
print("  Consumers  -> consumer1 / Consumer@123")
print("             -> consumer2 / Consumer@123")
print("             -> consumer3 / Consumer@123")
