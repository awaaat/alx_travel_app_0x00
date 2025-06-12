from .models import CustomUser, Listing, Booking, Payment, Review, Message
from rest_framework import serializers

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'user_id',
            'first_name',
            'last_name',
            'phone_number',
            'profile_image',
            'user_role',
            'bio',
        )
class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = (
            'property_id',
            'name',
            'host',
            'description',
            'location',
            'price_per_night',
            'created_at',
            'capacity',
            'amenities',
            'availability',
        )
class BookingSerializer(serializers.ModelSerializer):
    
    listing = ListingSerializer(read_only = True)
    user = CustomUserSerializer(read_only = True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = (
            'booking_id',
            'listing',
            'user',
            'start_date',
            'end_date',
            'booking_status',
            'created_at',
            'total_price'
        )
        
    def get_total_price(self, obj) -> float:
        return obj.get_total_price
        
    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end <= start:
            raise serializers.ValidationError("End date must be after start date.")
        listing = data.get('listing')
        if listing and not Listing.objects.filter(property_id=listing.property_id).exists():
            raise serializers.ValidationError("Invalid listing.")
        user = data.get('user')
        if user and not CustomUser.objects.filter(user_id=user.user_id, user_role='guest').exists():
            raise serializers.ValidationError("Invalid user or user is not a guest.")
        return data
        
class PaymentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only = True)
    booking = BookingSerializer(read_only = True)    
    class Meta:
        model = Payment
        fields = (
        'payment_id',
        'amount',
        'payment_date',
        'payment_method',
        'payment_status',
        'user',
        'booking',
        )
        
    def validate_amount(self, value):
        if value <= 0:
            serializers.ValidationError("Amount cannot be 0 or less than zero")
        return value
    def validate(self, data):
        booking = data.get('booking_id')
        amount = data.get('amount')
        if booking and amount and booking.total_price != amount:
            raise serializers.ValidationError("Payment amount must match booking total price.")
        return data
        
class ReviewSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only = True)
    listing = ListingSerializer(read_only = True)
    
    class Meta:
        model = Review
        fields = (
        'review_id',
        'review_date',
        'review_rating',
        'comment',
        'user',
        'listing',
        )
    def validate_review_rating(self, value):
        if not (1 <= value<= 5):
            raise serializers.ValidationError("Review Must be Between 1 - 5")
        return value
        
class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer(read_only = True)
    recipient = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Message
        fields = (
        'message_id',
        'sender',
        'recipient',
        'sent_at',
        'message_title',
        'message_body'
        )
    def validate_message_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be blank")
        return value

    def validate_message_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message title cannot be blank")
        return value
    
        