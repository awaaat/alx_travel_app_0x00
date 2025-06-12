from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.gis.db import models as gis_models
from django.utils import timezone
import uuid

# Phone number validator for international formats
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
)

class CustomUser(AbstractUser):
    """
    Represents a user in the application. Can be a guest, host, or admin.
    Uses UUID for primary key and includes timezone-aware fields.
    """
    class Meta:
        db_table = "app_user"

    user_id = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(null=False, blank=False, unique=True)
    phone_number = models.CharField(max_length=50, null=False, blank=False, validators=[phone_regex])
    user_role = models.CharField(
        choices=[('guest', 'Guest'), ('host', 'Host'), ('admin', 'Admin')],
        max_length=50, default='guest', null=False, blank=False
    )
    created_at = models.DateTimeField(default=timezone.now)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True, default='profiles/default.png')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user_role})"


class Listing(models.Model):
    """
    A property that can be booked. Only users with role 'host' can create listings.
    Includes geospatial location and availability tracking for AI-driven queries.
    """
    property_id = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4, editable=False)
    host = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                            limit_choices_to={'user_role': 'host'},
                            related_name='property_host')
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    location = models.CharField(max_length= 100, null=False, blank=False)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    property_images = models.ImageField(upload_to='property_images/', blank=True, null=True, default='property_images/default.jpg')
    capacity = models.PositiveIntegerField(null=False, blank=False, default=1, help_text="Maximum number of guests")
    amenities = models.JSONField(default=dict, blank=True, help_text="List of amenities (e.g., {'wifi': true, 'pool': false})")
    availability = models.JSONField(default=dict, blank=True, help_text="Availability calendar (e.g., {'2025-06-01': true})")

    def clean(self):
        if self.price_per_night <= 0:
            raise ValidationError("Price Cannot be 0.00")
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [models.Index(fields=['host', 'location'])]
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Booking(models.Model):
    """
    Stores bookings for listings. Prevents overlapping bookings and ensures date validity.
    Only users with role 'guest' can book.
    """
    booking_id = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                            limit_choices_to={'user_role': 'guest'},
                            related_name='property_guest')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    booking_status = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('CANCELLED', 'Cancelled')],
        null=False, blank=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    booking_payment = models.OneToOneField('Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='booking')

    def clean(self):
        """
        Validates that end_date is after start_date and prevents overlapping bookings.
        """
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date.")
        overlapping = Booking.objects.filter(
            listing=self.listing,
            end_date__gt=self.start_date,
            start_date__lt=self.end_date,
            booking_status__in=['PENDING', 'CONFIRMED']
        ).exclude(booking_id=self.booking_id)
        if overlapping.exists():
            raise ValidationError("This listing is already booked for the selected dates.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def get_total_price(self):
        """
        Calculates total price based on number of nights and listing rate.
        """
        stay_period = (self.end_date - self.start_date).days
        return self.listing.price_per_night * stay_period

    def approve(self, acting_user):
        """
        Admins can confirm bookings.
        """
        if acting_user.user_role != 'admin':
            raise PermissionError("Only admins can approve bookings.")
        if self.booking_status != 'PENDING':
            raise ValueError("Only pending bookings can be approved.")
        self.booking_status = 'CONFIRMED'
        self.save()
        return self

    def cancel(self, acting_user):
        """
        Booking can be cancelled by admin or the guest who made it.
        """
        is_admin = acting_user.user_role == 'admin'
        is_guest_owner = acting_user == self.user and acting_user.user_role == 'guest'
        if not (is_admin or is_guest_owner):
            raise PermissionError("Only the booking owner or an admin can cancel.")
        if self.booking_status == 'CANCELLED':
            raise ValueError("Booking is already cancelled.")
        self.booking_status = 'CANCELLED'
        self.save()
        return self

    def __str__(self):
        return f"User {self.user.first_name} has a Booking for {self.listing.name} with status {self.booking_status}"


class Payment(models.Model):
    """
    Stores payment details for a booking. One payment per booking.
    Includes status and transaction ID for integration with payment gateways.
    """
    payment_id = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4, editable=False)
    booking_id = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=50,
        choices=[('CREDIT CARD', 'Credit Card'), ('PAYPAL', 'PayPal'), ('MOBILE MONEY', 'Mobile Money'), ('STRIPE', 'Stripe')],
        null=False, blank=False
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('REFUNDED', 'Refunded')],
        default='PENDING',
        null=False,
        blank=False
    )
    transaction_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments')

    def __str__(self):
        return f"Payment from {self.user.first_name} for booking {self.booking_id.booking_id} ({self.payment_status})"


class Review(models.Model):
    """
    Stores a guest's review for a completed booking.
    Allows multiple reviews per guest for different bookings.
    """
    review_id = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                            limit_choices_to={'user_role': 'guest'},
                            related_name='reviews')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, null=True, blank=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    review_date = models.DateTimeField(default=timezone.now)
    review_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=1)
    comment = models.TextField(null=True, blank=True, max_length=250)
    is_approved = models.BooleanField(default=False, help_text="Indicates if review has been approved by admin")

    def __str__(self):
        return f"Property {self.listing.name} was awarded a {self.review_rating} review by {self.user.first_name}"


class Message(models.Model):
    """
    Stores a message sent between two users with read status and constraints.
    """
    message_id = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    sent_at = models.DateTimeField(auto_now_add=True)
    message_title = models.CharField(max_length=30, null=False, blank=False)
    message_body = models.TextField(max_length=1000, null=False, blank=False)
    is_read = models.BooleanField(default=False, help_text="Indicates if the message has been read")

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(sender=models.F('recipient')),
                name='prevent_self_messaging'
            )
        ]

    def __str__(self):
        return f"Message {self.message_title} from {self.sender} to {self.recipient}"