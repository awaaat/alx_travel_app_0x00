from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from listings.models import CustomUser, Listing, Booking, Payment, Review, Message
import uuid
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Seeds the database with sample data for the travel app'

    def handle(self, *args, **kwargs):
        # Clear existing data (optional, comment out to append)
        CustomUser.objects.all().delete()
        Listing.objects.all().delete()
        Booking.objects.all().delete()
        Payment.objects.all().delete()
        Review.objects.all().delete()
        Message.objects.all().delete()

        # Create 22 CustomUser entries (20 guests, 1 host, 1 admin)
        users = []
        user_data = [
            {"first_name": "Wanjiku", "last_name": "Muthoni", "email": "wanjiku.muthoni1@example.com", "phone": "+254712345601", "role": "guest", "bio": "Loves exploring Kenyan coast"},
            {"first_name": "Kamau", "last_name": "Njoroge", "email": "kamau.njoroge2@example.com", "phone": "+254712345602", "role": "guest", "bio": None},
            {"first_name": "Akinyi", "last_name": "Otieno", "email": "akinyi.otieno3@example.com", "phone": "+254712345603", "role": "guest", "bio": "Adventure enthusiast"},
            {"first_name": "Musa", "last_name": "Kipchoge", "email": "musa.kipchoge4@example.com", "phone": "+254712345604", "role": "guest", "bio": "Nature lover"},
            {"first_name": "Njeri", "last_name": "Wambui", "email": "njeri.wambui5@example.com", "phone": "+254712345605", "role": "guest", "bio": None},
            {"first_name": "Ochieng", "last_name": "Odhiambo", "email": "ochieng.odhiambo6@example.com", "phone": "+254712345606", "role": "guest", "bio": "Foodie and traveler"},
            {"first_name": "Wairimu", "last_name": "Kariuki", "email": "wairimu.kariuki7@example.com", "phone": "+254712345607", "role": "guest", "bio": None},
            {"first_name": "Kiptoo", "last_name": "Korir", "email": "kiptoo.korir8@example.com", "phone": "+254712345608", "role": "guest", "bio": "Wildlife enthusiast"},
            {"first_name": "Fatuma", "last_name": "Hassan", "email": "fatuma.hassan9@example.com", "phone": "+254712345609", "role": "guest", "bio": None},
            {"first_name": "Juma", "last_name": "Mwangi", "email": "juma.mwangi10@example.com", "phone": "+254712345610", "role": "guest", "bio": "Cultural explorer"},
            {"first_name": "Cherotich", "last_name": "Koech", "email": "cherotich.koech11@example.com", "phone": "+254712345611", "role": "guest", "bio": "Loves hiking"},
            {"first_name": "Mwenda", "last_name": "Githinji", "email": "mwenda.githinji12@example.com", "phone": "+254712345612", "role": "guest", "bio": None},
            {"first_name": "Auma", "last_name": "Ochieng", "email": "auma.ochieng13@example.com", "phone": "+254712345613", "role": "guest", "bio": "Beach enthusiast"},
            {"first_name": "Kipkurui", "last_name": "Rono", "email": "kipkurui.rono14@example.com", "phone": "+254712345614", "role": "guest", "bio": None},
            {"first_name": "Wambui", "last_name": "Njuguna", "email": "wambui.njuguna15@example.com", "phone": "+254712345615", "role": "guest", "bio": "City explorer"},
            {"first_name": "Ahmed", "last_name": "Mohamed", "email": "ahmed.mohamed16@example.com", "phone": "+254712345616", "role": "guest", "bio": None},
            {"first_name": "Wanjiru", "last_name": "Mbugua", "email": "wanjiru.mbugua17@example.com", "phone": "+254712345617", "role": "guest", "bio": "Cultural enthusiast"},
            {"first_name": "Onyango", "last_name": "Oluoch", "email": "onyango.oluoch18@example.com", "phone": "+254712345618", "role": "guest", "bio": None},
            {"first_name": "Zawadi", "last_name": "Karanja", "email": "zawadi.karanja19@example.com", "phone": "+254712345619", "role": "guest", "bio": "Nature lover"},
            {"first_name": "Shakira", "last_name": "Omondi", "email": "shakira.omondi20@example.com", "phone": "+254712345620", "role": "guest", "bio": "Travel enthusiast"},
            {"first_name": "Mumbi", "last_name": "Ngugi", "email": "mumbi.ngugi21@example.com", "phone": "+254712345621", "role": "host", "bio": "Hosts cozy cottages"},
            {"first_name": "Mary", "last_name": "Wanjala", "email": "mary.wanjala22@example.com", "phone": "+254712345622", "role": "admin", "bio": "Platform administrator"}
        ]

        for i, data in enumerate(user_data):
            user = CustomUser.objects.create(
                user_id=uuid.uuid4(),
                username=f"user{i+1}",
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                password_hash=make_password("password123"),
                phone_number=data["phone"],
                user_role=data["role"],
                created_at=datetime(2025, 1, 1 + i),
                bio=data["bio"],
                profile_image=f"profiles/user{i+1}.jpg"
            )
            users.append(user)

        # Create 20 Listing entries
        listings = []
        hosts = [u for u in users if u.user_role == "host"]
        listing_data = [
            {"name": "Nairobi Skyline Apartment", "location": "Nairobi, Kenya", "price": 7500.00, "desc": "Modern apartment in Westlands"},
            {"name": "Mombasa Beach Villa", "location": "Mombasa, Kenya", "price": 12000.00, "desc": "Beachfront villa with ocean views"},
            {"name": "Maasai Mara Safari Lodge", "location": "Narok, Kenya", "price": 20000.00, "desc": "Luxury lodge near game reserve"},
            {"name": "Diani Beach Cottage", "location": "Diani, Kenya", "price": 8500.00, "desc": "Cozy cottage steps from the beach"},
            {"name": "Naivasha Lake House", "location": "Naivasha, Kenya", "price": 9500.00, "desc": "Scenic lakefront property"},
            {"name": "Kisumu City Loft", "location": "Kisumu, Kenya", "price": 6000.00, "desc": "Modern loft in the city center"},
            {"name": "Lamu Island Retreat", "location": "Lamu, Kenya", "price": 15000.00, "desc": "Traditional Swahili-style house"},
            {"name": "Eldoret Farmhouse", "location": "Eldoret, Kenya", "price": 7000.00, "desc": "Rustic farmhouse with gardens"},
            {"name": "Nyeri Hill Cabin", "location": "Nyeri, Kenya", "price": 8000.00, "desc": "Cabin with Aberdare views"},
            {"name": "Nakuru Eco-Lodge", "location": "Nakuru, Kenya", "price": 11000.00, "desc": "Eco-friendly lodge near Lake Nakuru"},
            {"name": "Nairobi Urban Studio", "location": "Nairobi, Kenya", "price": 6500.00, "desc": "Compact studio in Kilimani"},
            {"name": "Malindi Oceanfront", "location": "Malindi, Kenya", "price": 13000.00, "desc": "Spacious villa by the sea"},
            {"name": "Amboseli Safari Camp", "location": "Kajiado, Kenya", "price": 18000.00, "desc": "Camp with Kilimanjaro views"},
            {"name": "Watamu Beach House", "location": "Watamu, Kenya", "price": 9000.00, "desc": "Charming house near coral reefs"},
            {"name": "Nanyuki Ranch House", "location": "Nanyuki, Kenya", "price": 10000.00, "desc": "Ranch-style home near Mt. Kenya"},
            {"name": "Kisii Hills Cottage", "location": "Kisii, Kenya", "price": 5500.00, "desc": "Quiet cottage in the hills"},
            {"name": "Thika Modern Villa", "location": "Thika, Kenya", "price": 8500.00, "desc": "Villa with modern amenities"},
            {"name": "Machakos Retreat", "location": "Machakos, Kenya", "price": 7000.00, "desc": "Secluded retreat with views"},
            {"name": "Kericho Tea Farmhouse", "location": "Kericho, Kenya", "price": 7500.00, "desc": "Farmhouse amidst tea plantations"},
            {"name": "Voi Safari Lodge", "location": "Voi, Kenya", "price": 12000.00, "desc": "Lodge near Tsavo National Park"}
        ]

        for i, data in enumerate(listing_data):
            listing = Listing.objects.create(
                property_id=uuid.uuid4(),
                host=hosts[i % len(hosts)],
                name=data["name"],
                description=data["desc"],
                location=data["location"],
                price_per_night=data["price"],
                created_at=datetime(2025, 2, 1 + i),
                updated_at=datetime(2025, 2, 1 + i),
                property_images=f"property_images/listing{i+1}.jpg"
            )
            listings.append(listing)

        # Create 20 Booking entries
        guests = [u for u in users if u.user_role == "guest"]
        bookings = []
        booking_data = [
            {"start_date": datetime(2025, 3, 1), "end_date": datetime(2025, 3, 5), "status": "PENDING"},
            {"start_date": datetime(2025, 3, 2), "end_date": datetime(2025, 3, 7), "status": "CONFIRMED"},
            {"start_date": datetime(2025, 3, 3), "end_date": datetime(2025, 3, 6), "status": "CANCELLED"},
            {"start_date": datetime(2025, 3, 4), "end_date": datetime(2025, 3, 8), "status": "PENDING"},
            {"start_date": datetime(2025, 3, 5), "end_date": datetime(2025, 3, 10), "status": "CONFIRMED"},
            {"start_date": datetime(2025, 3, 6), "end_date": datetime(2025, 3, 9), "status": "CANCELLED"},
            {"start_date": datetime(2025, 3, 7), "end_date": datetime(2025, 3, 12), "status": "PENDING"},
            {"start_date": datetime(2025, 3, 8), "end_date": datetime(2025, 3, 11), "status": "CONFIRMED"},
            {"start_date": datetime(2025, 3, 9), "end_date": datetime(2025, 3, 14), "status": "CANCELLED"},
            {"start_date": datetime(2025, 3, 10), "end_date": datetime(2025, 3, 15), "status": "PENDING"},
            {"start_date": datetime(2025, 3, 11), "end_date": datetime(2025, 3, 16), "status": "CONFIRMED"},
            {"start_date": datetime(2025, 3, 12), "end_date": datetime(2025, 3, 17), "status": "CANCELLED"},
            {"start_date": datetime(2025, 3, 13), "end_date": datetime(2025, 3, 18), "status": "PENDING"},
            {"start_date": datetime(2025, 3, 14), "end_date": datetime(2025, 3, 19), "status": "CONFIRMED"},
            {"start_date": datetime(2025, 3, 15), "end_date": datetime(2025, 3, 20), "status": "CANCELLED"},
            {"start_date": datetime(2025, 3, 16), "end_date": datetime(2025, 3, 21), "status": "PENDING"},
            {"start_date": datetime(2025, 3, 17), "end_date": datetime(2025, 3, 22), "status": "CONFIRMED"},
            {"start_date": datetime(2025, 3, 18), "end_date": datetime(2025, 3, 23), "status": "CANCELLED"},
            {"start_date": datetime(2025, 3, 19), "end_date": datetime(2025, 3, 24), "status": "PENDING"},
            {"start_date": datetime(2025, 3, 20), "end_date": datetime(2025, 3, 25), "status": "CONFIRMED"}
        ]

        for i, data in enumerate(booking_data):
            listing = listings[i % len(listings)]
            total_price = listing.price_per_night * (data["end_date"] - data["start_date"]).days
            booking = Booking.objects.create(
                booking_id=uuid.uuid4(),
                listing=listing,
                user=guests[i % len(guests)],  # Use modulo to cycle through guests
                start_date=data["start_date"],
                end_date=data["end_date"],
                booking_status=data["status"],
                created_at=data["start_date"],
                total_price=total_price
            )
            bookings.append(booking)

        # Create 20 Payment entries
        payment_data = [
            {"method": "CREDIT CARD", "date": datetime(2025, 3, i + 1)} for i in range(5)
        ] + [
            {"method": "PAYPAL", "date": datetime(2025, 3, i + 6)} for i in range(5)
        ] + [
            {"method": "MOBILE MONEY", "date": datetime(2025, 3, i + 11)} for i in range(5)
        ] + [
            {"method": "STRIPE", "date": datetime(2025, 3, i + 16)} for i in range(5)
        ]

        for i, data in enumerate(payment_data):
            booking = bookings[i]
            payment = Payment.objects.create(
                payment_id=uuid.uuid4(),
                booking_id=booking,
                amount=booking.total_price,
                payment_date=data["date"],
                payment_method=data["method"],
                user=booking.user
            )

        # Create 20 Review entries
        review_data = [
            {"rating": 4, "comment": "Great stay, very comfortable!", "date": datetime(2025, 4, 1)},
            {"rating": 5, "comment": "Amazing views and hospitality", "date": datetime(2025, 4, 2)},
            {"rating": 3, "comment": None, "date": datetime(2025, 4, 3)},
            {"rating": 4, "comment": "Clean and cozy place", "date": datetime(2025, 4, 4)},
            {"rating": 5, "comment": "Perfect for a getaway", "date": datetime(2025, 4, 5)},
            {"rating": 2, "comment": "Could be better maintained", "date": datetime(2025, 4, 6)},
            {"rating": 4, "comment": None, "date": datetime(2025, 4, 7)},
            {"rating": 5, "comment": "Loved the location!", "date": datetime(2025, 4, 8)},
            {"rating": 3, "comment": "Decent but noisy area", "date": datetime(2025, 4, 9)},
            {"rating": 4, "comment": "Friendly host, great stay", "date": datetime(2025, 4, 10)},
            {"rating": 5, "comment": None, "date": datetime(2025, 4, 11)},
            {"rating": 4, "comment": "Very relaxing environment", "date": datetime(2025, 4, 12)},
            {"rating": 3, "comment": "Good but limited amenities", "date": datetime(2025, 4, 13)},
            {"rating": 5, "comment": "Exceeded expectations!", "date": datetime(2025, 4, 14)},
            {"rating": 4, "comment": None, "date": datetime(2025, 4, 15)},
            {"rating": 2, "comment": "Issues with booking process", "date": datetime(2025, 4, 16)},
            {"rating": 4, "comment": "Comfortable and scenic", "date": datetime(2025, 4, 17)},
            {"rating": 5, "comment": "Best stay in Kenya!", "date": datetime(2025, 4, 18)},
            {"rating": 3, "comment": None, "date": datetime(2025, 4, 19)},
            {"rating": 4, "comment": "Great value for money", "date": datetime(2025, 4, 20)}
        ]

        for i, data in enumerate(review_data):
            booking = bookings[i]
            review = Review.objects.create(
                review_id=uuid.uuid4(),
                user=guests[i % len(guests)],  # Use modulo to cycle through guests
                property_listing=booking.listing,
                review_date=data["date"],
                review_rating=data["rating"],
                comment=data["comment"]
            )

        # Create 20 Message entries
        message_data = [
            {"title": "Booking Inquiry", "body": "Is your property available next week?", "date": datetime(2025, 5, 1)},
            {"title": "Check-in Details", "body": "Please provide check-in instructions.", "date": datetime(2025, 5, 2)},
            {"title": "Property Questions", "body": "Does the villa have Wi-Fi?", "date": datetime(2025, 5, 3)},
            {"title": "Reservation Request", "body": "Can you reserve for 3 nights?", "date": datetime(2025, 5, 4)},
            {"title": "Amenities Info", "body": "Is there a pool at the lodge?", "date": datetime(2025, 5, 5)},
            {"title": "Payment Confirmation", "body": "Payment sent, please confirm.", "date": datetime(2025, 5, 6)},
            {"title": "Late Check-out", "body": "Can I check out late?", "date": datetime(2025, 5, 7)},
            {"title": "Property Feedback", "body": "Great stay, thanks!", "date": datetime(2025, 5, 8)},
            {"title": "Booking Change", "body": "Need to change dates to next month.", "date": datetime(2025, 5, 9)},
            {"title": "Host Response", "body": "Yes, Wi-Fi is available.", "date": datetime(2025, 5, 10)},
            {"title": "Availability Check", "body": "Is the cottage free in April?", "date": datetime(2025, 5, 11)},
            {"title": "Guest Request", "body": "Can you provide extra towels?", "date": datetime(2025, 5, 12)},
            {"title": "Confirmation", "body": "Booking confirmed, see you soon!", "date": datetime(2025, 5, 13)},
            {"title": "Location Query", "body": "How far is the lodge from town?", "date": datetime(2025, 5, 14)},
            {"title": "Cancellation Request", "body": "Need to cancel my booking.", "date": datetime(2025, 5, 15)},
            {"title": "Special Request", "body": "Can you arrange airport pickup?", "date": datetime(2025, 5, 16)},
            {"title": "Property Details", "body": "Is parking available?", "date": datetime(2025, 5, 17)},
            {"title": "Thank You", "body": "Thanks for a great stay!", "date": datetime(2025, 5, 18)},
            {"title": "Follow-up", "body": "Any discounts for repeat guests?", "date": datetime(2025, 5, 19)},
            {"title": "Host Inquiry", "body": "Please confirm booking details.", "date": datetime(2025, 5, 20)}
        ]

        for i, data in enumerate(message_data):
            sender = users[i % len(users)]
            recipient = users[(i + 1) % len(users)]
            message = Message.objects.create(
                message_id=uuid.uuid4(),
                sender=sender,
                recipient=recipient,
                sent_at=data["date"],
                message_title=data["title"],
                message_body=data["body"]
            )

        self.stdout.write(self.style.SUCCESS("Database seeded with 20 entries per table."))