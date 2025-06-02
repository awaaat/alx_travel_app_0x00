from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status, filters
from .models import *
from .serializers import *

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name'] 
    ordering_fields = ['-created_at']
    
    #We comment out the below, it is a repeat. ModelViewSet already handles CRUD operations
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    """

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.filter(price_per_night__gt = 0)
    serializer_class = ListingSerializer
    search_fields = ['name', 'location', 'price_per_night']
    ordering_fields = ['-created_at']
    
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    search_fields = ['created_at', 'booking_status', 'start_date']
    ordering_fields = ['-created_at']
    
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    search_fields = ['user']
    ordering_fields = ['-payment_date']
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    search_fields = ['listing', 'review_date', 'review_rating', 'comment']
    ordering_fields = ['review_rating']
    
    
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    search_fields = ['message_title']
    ordering_fields = ['sent_at']
        


@api_view(['GET'])
def index(request):
    return Response({"message": "Welcome to ALX Travel App!"})
