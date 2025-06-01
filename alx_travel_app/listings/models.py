from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid
from datetime import timezone

class CustomUser(AbstractUser):
    class Meta:
        db_table = "app_user"
        
    user_id = models.UUIDField(primary_key=True, db_index=True, 
                            default=uuid.uuid4, editable=False
                            )
    first_name = models.CharField(max_length=100, null=False, 
                                editable=True,blank=False)
    last_name = models.CharField(max_length=100, null=False, 
                                editable=True, blank=False)
    email = models.EmailField(null=False, editable=False, 
                            blank=False)
    password_hash = models.CharField(max_length=255, null=False,
                                    blank=False, editable=False)
    phone_number = models.CharField(max_length=50, null = False, 
                                    blank=False, editable= True)
    user_role = models.CharField(choices = [('guest', 'Guest'), ('host', 'Host'), ('admin', 'Admin')], 
                                max_length=50, default='guest', null=False, blank = False)
    created_at = models.DateField(auto_now_add=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank = True, null = True)
    
        
class Listing(models.Model):
    property_id = models.UUIDField(primary_key=True, db_index=True, 
                            default=uuid.uuid4, editable=False)
    host = models.ForeignKey(to = CustomUser, on_delete= models.CASCADE,
                            limit_choices_to= {'user_role': 'host'},
                            related_name = 'property_host')
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    location = models.CharField(max_length=200, null=False, blank=False)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now=True)
    property_images = models.ImageField(blank=False, null = False, upload_to='property_images/')
    
    class Meta:
        indexes = [models.Index(fields=['host', 'location'])]
        ordering = ['-created_at']
        
class Booking(models.Model):
    booking_id = models.UUIDField(primary_key=True, db_index=True, 
                            default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(to = Listing, on_delete= models.CASCADE
                                    )
    user = models.ForeignKey(to = CustomUser, on_delete=models.CASCADE, 
                            limit_choices_to= {'user_role': 'guest'}, 
                            related_name= 'property_guest')
    start_date = models.DateField(blank=False, null  = False)
    end_date = models.DateField(blank = False, null = False)
    booking_status = models.CharField(max_length= 20,
                                    choices=[('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('CANCELLED', 'Cancelled')], 
                                    null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, blank= False, null=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    
    @property
    def get_total_price(self):
        stay_period = int((self.end_date - self.start_date).days)
        return self.listing.price_per_night * stay_period
    
    def approve(self, acting_user):
        if acting_user.user_role != 'admin':
            raise PermissionError("Only admins can approve bookings.")
        if self.booking_status != 'PENDING':
            raise ValueError("Only pending bookings can be approved.")
        self.booking_status = 'CONFIRMED'
        self.save()
        return self

def cancel(self, acting_user):
    is_admin = acting_user.user_role == 'admin'
    is_guest_owner = acting_user == self.user and acting_user.user_role == 'guest'
    if not (is_admin or is_guest_owner):
        raise PermissionError("Only the booking owner or an admin can cancel.")
    if self.booking_status == 'CANCELLED':
        raise ValueError("Booking is already cancelled.")
    self.booking_status = 'CANCELLED'
    self.save()
    return self
    
    def __str__(self) -> str:
        return f"User {self.user.first_name} has a Booking for {self.listing.name} with status {self.booking_status}"
    

class Payment(models.Model):
    payment_id = models.UUIDField(primary_key=True, db_index=True, 
                            default=uuid.uuid4, editable=False)
    booking_id = models.OneToOneField(to = Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length= 50, choices=[('CREDIT CARD', 'credit card'),
                                            ('PAYPAL', 'paypal'), ('MOBILE MONEY', 'mobile money'), 
                                            ('STRIPE', 'stripe')], null=False, blank=False)
    user = models.ForeignKey(to = CustomUser, on_delete= models.CASCADE,
                            limit_choices_to ={'user_role':'guest'})
    
    def __str__(self):
        return f"Payment from {self.user.first_name} for booking {self.booking_id.booking_id}"

class Review(models.Model):
    review_id = models.UUIDField(primary_key=True, db_index=True, 
                            default=uuid.uuid4, editable=False)
    user = models.OneToOneField(to = CustomUser, on_delete= models.CASCADE, 
                                limit_choices_to = {'user_role': 'guest'})
    property_listing = models.ForeignKey(to = Listing, on_delete= models.CASCADE)
    review_date = models.DateTimeField(auto_now_add=True)
    review_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=1, 
                                        blank=False, null= False)
    comment = models.TextField(null = True, blank=True)
    
    def __str__(self):
        return f"Property {self.property_listing.name} was awarded a {self.review_rating} review by {self.user.first_name}"
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, db_index=True, 
                            default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(CustomUser, on_delete= models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    sent_at = models.DateTimeField(auto_now_add=True)
    message_title = models.TextField(null=False, blank=False, max_length=30)
    message_body = models.TextField(null=False, blank=False)
    
    def __str__(self) -> str:
        return f"Message {self.message_title} from {self.sender}"