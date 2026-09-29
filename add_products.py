import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from catalog.models import Category, Product
from users.models import UserProfile

User = get_user_model()

# Get or create user Optimus23
user, created = User.objects.get_or_create(username="Optimus23")
if created:
    user.set_password("admin123")
    user.save()
    UserProfile.objects.create(user=user, role="retailer")
    print("User Optimus23 created as retailer")
else:
    user.set_password("admin123")
    user.save()
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.role = "retailer"
    profile.save()
    print(f"User Optimus23 already exists, role set to: {profile.role}")

elec     = Category.objects.get(slug="electronics")
clothing = Category.objects.get(slug="clothing")
books    = Category.objects.get(slug="books")
home     = Category.objects.get(slug="home")

products = [
    {
        "name": "Samsung 65-inch 4K OLED TV",
        "description": "Crystal clear 4K OLED display with Smart TV features, HDR support and built-in streaming apps.",
        "price": 89999,
        "stock": 15,
        "category": elec,
    },
    {
        "name": "Apple AirPods Pro 2",
        "description": "Active Noise Cancellation, Adaptive Transparency, Personalized Spatial Audio, MagSafe charging case.",
        "price": 24999,
        "stock": 50,
        "category": elec,
    },
    {
        "name": "Men Classic Polo T-Shirt",
        "description": "Premium 100% cotton polo shirt, comfortable fit, available in all sizes.",
        "price": 999,
        "stock": 200,
        "category": clothing,
    },
    {
        "name": "The Pragmatic Programmer",
        "description": "Your journey to mastery. Timeless lessons on software development and craftsmanship.",
        "price": 1499,
        "stock": 75,
        "category": books,
    },
    {
        "name": "Philips Air Fryer HD9200",
        "description": "Rapid Air technology, 4.1L capacity, digital touch panel, uses up to 90% less fat.",
        "price": 8499,
        "stock": 30,
        "category": home,
    },
]

for p in products:
    prod, was_created = Product.objects.get_or_create(
        name=p["name"],
        defaults={**p, "retailer": user}
    )
    print(f"{'Created' if was_created else 'Already exists'}: {prod.name}")

print("\nDone!")
