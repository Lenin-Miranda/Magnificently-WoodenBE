from .models import Order, OrderItem
from .serializer import OrderSerializer, OrderItemSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser


#----- USER VIEWS -----
from rest_framework import status

class OrderListView(generics.ListCreateAPIView):
    '''
    List all orders for the logged in user
    '''

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
class OrderDetailView(generics.RetrieveAPIView):
    '''
    Retrieve a specific order for the logged in user
    '''

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    lookup_field = 'id'

"""OrderCreateView removed: creation handled by ListCreateAPIView above."""

#----- ADMIN VIEWS -----
from rest_framework.pagination import PageNumberPagination

class AdminOrderListView(generics.ListAPIView):
    '''
    List all orders (admin only)
    '''

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    pagination_class = PageNumberPagination

class AdminOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    '''
    Retrieve / update / delete a specific order (admin only)
    '''

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

class AdminOrderUpdateView(generics.UpdateAPIView):
    '''
    Update a specific order (admin only)
    '''

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

class AdminOrderDeleteView(generics.DestroyAPIView):
    '''
    Delete a specific order (admin only)
    '''

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

class AdminOrderItemListView(generics.ListAPIView):
    '''
    List all order items (admin only)
    '''

    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAdminUser]

class AdminOrderItemDetailView(generics.RetrieveAPIView):
    '''
    Retrieve a specific order item (admin only)
    '''

    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'