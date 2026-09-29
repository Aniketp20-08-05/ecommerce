from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import CheckoutSerializer, OrderSerializer, StatusUpdateSerializer
from .services import CheckoutError, cancel_order, change_status, place_order


class OrderListCreateView(APIView):
    @extend_schema(responses=OrderSerializer(many=True))
    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related("items__product")
        return Response(OrderSerializer(orders, many=True).data)

    @extend_schema(request=CheckoutSerializer, responses={201: OrderSerializer})
    def post(self, request):
        """Checkout: turns the current cart into an order. Needs shipping details."""
        ser = CheckoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            order = place_order(request.user, ser.validated_data)
        except CheckoutError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    @extend_schema(responses=OrderSerializer)
    def get(self, request, pk):
        order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=pk, user=request.user)
        return Response(OrderSerializer(order).data)


class OrderCancelView(APIView):
    @extend_schema(request=None, responses=OrderSerializer)
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        try:
            order = cancel_order(order)
        except CheckoutError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)


class OrderStatusView(APIView):
    """Staff only: move an order through paid -> shipped -> delivered (or cancel it)."""
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(request=StatusUpdateSerializer, responses=OrderSerializer)
    def patch(self, request, pk):
        ser = StatusUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        order = get_object_or_404(Order, pk=pk)
        try:
            order = change_status(order, ser.validated_data["status"])
        except CheckoutError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)
