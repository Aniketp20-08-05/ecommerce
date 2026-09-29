from rest_framework import permissions, viewsets

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class ReadOnlyOrAdmin(permissions.BasePermission):
    """Anyone can browse; only staff can create/update/delete."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

class IsRetailerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user and request.user.is_authenticated:
            if request.user.is_staff:
                return True
            if hasattr(request.user, 'profile') and request.user.profile.role == 'retailer':
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        return obj.retailer == request.user


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAdmin]


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsRetailerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(retailer=self.request.user)

    def get_queryset(self):
        qs = Product.objects.select_related("category")
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        category = self.request.query_params.get("category")
        search = self.request.query_params.get("search")
        if category:
            qs = qs.filter(category_id=category)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs
