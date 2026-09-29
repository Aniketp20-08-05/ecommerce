from django.db.models import F
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import AddToCartSerializer, CartItemSerializer, CartSerializer


def get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartView(APIView):
    @extend_schema(responses=CartSerializer)
    def get(self, request):
        cart = get_cart(request.user)
        return Response(CartSerializer(cart).data)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request):
        get_cart(request.user).items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemsView(APIView):
    @extend_schema(request=AddToCartSerializer, responses={201: CartItemSerializer})
    def post(self, request):
        ser = AddToCartSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        cart = get_cart(request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product_id=ser.validated_data["product_id"],
            defaults={"quantity": ser.validated_data["quantity"]},
        )
        if not created:
            item.quantity = F("quantity") + ser.validated_data["quantity"]
            item.save(update_fields=["quantity"])
            item.refresh_from_db()
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    def _item(self, request, pk):
        return get_object_or_404(CartItem, pk=pk, cart__user=request.user)

    @extend_schema(request=None, responses=CartItemSerializer)
    def patch(self, request, pk):
        item = self._item(request, pk)
        qty = request.data.get("quantity")
        if not isinstance(qty, int) or qty < 1:
            return Response({"quantity": "Must be an integer >= 1."}, status=400)
        item.quantity = qty
        item.save(update_fields=["quantity"])
        return Response(CartItemSerializer(item).data)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, pk):
        self._item(request, pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
