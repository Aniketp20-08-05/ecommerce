from django.urls import path

from .views import OrderCancelView, OrderDetailView, OrderListCreateView, OrderStatusView

urlpatterns = [
    path("", OrderListCreateView.as_view(), name="orders"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("<int:pk>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
    path("<int:pk>/status/", OrderStatusView.as_view(), name="order-status"),
]
