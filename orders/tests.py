from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from catalog.models import Category, Product

User = get_user_model()

SHIPPING = {
    "ship_name": "Asha Verma",
    "ship_phone": "9876543210",
    "ship_address": "12, MG Road",
    "ship_city": "Indore",
    "ship_state": "Madhya Pradesh",
    "ship_pincode": "452001",
}


class ShopFlowTests(APITestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Books", slug="books")
        self.book = Product.objects.create(category=self.cat, name="Python 101", price=Decimal("250.00"), stock=5)
        self.user = User.objects.create_user("asha", "a@x.com", "S3curePass!word")
        self.login("asha")

    def login(self, username):
        token = self.client.post(reverse("token_obtain"), {"username": username, "password": "S3curePass!word"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def add(self, qty):
        return self.client.post(reverse("cart-items"), {"product_id": self.book.id, "quantity": qty})

    def checkout(self, **overrides):
        return self.client.post(reverse("orders"), {**SHIPPING, **overrides})

    def test_requires_jwt(self):
        self.client.credentials()
        self.assertEqual(self.client.get(reverse("cart")).status_code, 401)

    def test_health_check_is_public(self):
        self.client.credentials()
        self.assertEqual(self.client.get(reverse("health")).data, {"status": "ok"})

    def test_register(self):
        self.client.credentials()
        r = self.client.post(reverse("register"), {"username": "ravi", "email": "r@x.com", "password": "S3curePass!word"})
        self.assertEqual(r.status_code, 201)
        self.assertNotIn("password", r.data)

    def test_checkout_reduces_stock_and_clears_cart(self):
        self.add(2)
        r = self.checkout()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Decimal(r.data["total"]), Decimal("500.00"))
        self.assertEqual(r.data["ship_city"], "Indore")
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 3)
        self.assertEqual(self.client.get(reverse("cart")).data["items"], [])

    def test_checkout_validates_shipping(self):
        self.add(1)
        self.assertEqual(self.checkout(ship_phone="12345").status_code, 400)
        self.assertEqual(self.checkout(ship_pincode="00000").status_code, 400)
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 5)  # nothing was taken

    def test_cannot_oversell(self):
        self.add(9)
        self.assertEqual(self.checkout().status_code, 400)
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 5)

    def test_cancel_restores_stock_once(self):
        self.add(2)
        oid = self.checkout().data["id"]
        self.assertEqual(self.client.post(reverse("order-cancel", args=[oid])).status_code, 200)
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 5)
        self.assertEqual(self.client.post(reverse("order-cancel", args=[oid])).status_code, 400)

    def test_user_cannot_see_others_orders(self):
        self.add(1)
        oid = self.checkout().data["id"]
        User.objects.create_user("other", "o@x.com", "S3curePass!word")
        self.login("other")
        self.assertEqual(self.client.get(reverse("order-detail", args=[oid])).status_code, 404)

    def test_only_staff_can_create_products(self):
        r = self.client.post(reverse("product-list"), {"category": self.cat.id, "name": "X", "price": "10", "stock": 1})
        self.assertEqual(r.status_code, 403)

    def test_status_lifecycle_and_shipped_orders_cannot_be_cancelled(self):
        self.add(1)
        oid = self.checkout().data["id"]
        # customers cannot change status
        self.assertEqual(self.client.patch(reverse("order-status", args=[oid]), {"status": "paid"}).status_code, 403)
        # staff moves it along
        User.objects.create_superuser("boss", "b@x.com", "S3curePass!word")
        self.login("boss")
        url = reverse("order-status", args=[oid])
        self.assertEqual(self.client.patch(url, {"status": "delivered"}).status_code, 400)  # can't skip steps
        self.assertEqual(self.client.patch(url, {"status": "paid"}).status_code, 200)
        self.assertEqual(self.client.patch(url, {"status": "shipped"}).status_code, 200)
        # customer can no longer cancel
        self.login("asha")
        self.assertEqual(self.client.post(reverse("order-cancel", args=[oid])).status_code, 400)

    def test_staff_cancel_restocks(self):
        self.add(3)
        oid = self.checkout().data["id"]
        User.objects.create_superuser("boss", "b@x.com", "S3curePass!word")
        self.login("boss")
        self.assertEqual(self.client.patch(reverse("order-status", args=[oid]), {"status": "cancelled"}).status_code, 200)
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 5)
