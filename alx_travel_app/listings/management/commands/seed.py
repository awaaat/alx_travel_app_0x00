from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.contrib.gis.geos import Point
from listings.models import CustomUser, Listing, Booking, Payment, Review, Message
import uuid
from datetime import datetime, timedelta
from faker import Faker
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds the database with sample data for the travel app'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=1000, help='Number of CustomUser entries')
        parser.add_argument('--listings', type=int, default=2000, help='Number of Listing entries')
        parser.add_argument('--bookings', type=int, default=5000, help='Number of Booking entries')
        parser.add_argument('--payments', type=int, default=800, help='Number of Payment entries')
        parser.add_argument('--reviews', type=int, default=800, help='Number of Review entries')
        parser.add_argument('--messages', type=int, default=6000, help='Number of Message entries')

    def handle(self, *args, **kwargs):
        fake = Faker('en_US')  # Use en_US as en_KE is not available in Faker
        Faker.seed(0)  # Ensure reproducible data

        num_users = max(kwargs['users'], 1000)
        num_listings = max(kwargs['listings'], 2000)
        num_bookings = max(kwargs['bookings'], 5000)
        num_payments = max(kwargs['payments'], 800)
        num_reviews = max(kwargs['reviews'], 800)
        num_messages = max(kwargs['messages'], 6000)

        # Fix invalid created_at values in CustomUser before deletion
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE app_user
                SET created_at = DATE_FORMAT(created_at, '%%Y-%%m-%%d 00:00:00')
                WHERE created_at IS NOT NULL
                AND created_at NOT LIKE '%%T%%';
            """)

        # Clear existing data
        CustomUser.objects.all().delete()
        Listing.objects.all().delete()
        Booking.objects.all().delete()
        Payment.objects.all().delete()
        Review.objects.all().delete()
        Message.objects.all().delete()

        # Kenyan locations with approximate coordinates
        kenyan_locations = {
            "Nairobi": (36.8219, -1.2921), "Mombasa": (39.6682, -4.0435), "Diani": (39.5948, -4.2978),
            "Naivasha": (36.4359, -0.7172), "Kisumu": (34.7617, -0.0917), "Lamu": (40.9020, -2.2717),
            "Eldoret": (35.2698, 0.5143), "Nyeri": (36.9476, -0.4201), "Nakuru": (36.0800, -0.3031),
            "Malindi": (40.1169, -3.2192), "Amboseli": (37.2531, -2.6450), "Watamu": (40.0170, -3.3547),
            "Nanyuki": (37.0728, 0.0162), "Kisii": (34.7667, -0.6817), "Thika": (37.0834, -1.0333),
            "Machakos": (37.2652, -1.5209), "Kericho": (35.2831, -0.3662), "Voi": (38.5561, -3.3960),
            "Kitale": (35.0062, 1.0157), "Garissa": (39.6583, 0.4532)
        }

        # Amenities options
        amenities_options = [
            {"wifi": True, "pool": False, "parking": True, "air_conditioning": False},
            {"wifi": True, "pool": True, "parking": True, "air_conditioning": True},
            {"wifi": False, "pool": False, "parking": True, "air_conditioning": False},
            {"wifi": True, "pool": True, "parking": False, "air_conditioning": True}
        ]

        # Create CustomUser entries (80% guests, 15% hosts, 5% admins)
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

        # Generate additional user entries
        for i in range(22, num_users):
            role = 'guest' if i < int(num_users * 0.8) else 'host' if i < int(num_users * 0.95) else 'admin'
            bio = fake.sentence(nb_words=5) if random.choice([True, False]) else None
            user_data.append({
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": f"{fake.user_name()}{i+1}@example.com",
                "phone": f"+254{random.randint(700000000, 799999999)}",
                "role": role,
                "bio": bio
            })

        for i, data in enumerate(user_data):
            user = CustomUser.objects.create(
                user_id=uuid.uuid4(),
                username=f"user{i+1}",
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                password=make_password("testPass"),
                phone_number=data["phone"],
                user_role=data["role"],
                created_at=timezone.make_aware(datetime(2025, 1, 1, 0, 0, 0) + timedelta(days=i)),
                bio=data["bio"],
                profile_image=f"profiles/user{i+1}.jpg" if random.choice([True, False]) else None
            )
            users.append(user)

        # Create Listing entries
        listings = []
        hosts = [u for u in users if u.user_role == "host"]
        listing_data = [
            {"name": "Nairobi Skyline Apartment", "location": "Nairobi", "coords": kenyan_locations["Nairobi"], "price": 7500.00, "desc": "Modern apartment in Westlands", "capacity": 4},
            {"name": "Mombasa Beach Villa", "location": "Mombasa", "coords": kenyan_locations["Mombasa"], "price": 12000.00, "desc": "Beachfront villa with ocean views", "capacity": 6},
            {"name": "Maasai Mara Safari Lodge", "location": "Narok", "coords": kenyan_locations["Amboseli"], "price": 20000.00, "desc": "Luxury lodge near game reserve", "capacity": 8},
            {"name": "Diani Beach Cottage", "location": "Diani", "coords": kenyan_locations["Diani"], "price": 8500.00, "desc": "Cozy cottage steps from the beach", "capacity": 3},
            {"name": "Naivasha Lake House", "location": "Naivasha", "coords": kenyan_locations["Naivasha"], "price": 9500.00, "desc": "Scenic lakefront property", "capacity": 5},
            {"name": "Kisumu City Loft", "location": "Kisumu", "coords": kenyan_locations["Kisumu"], "price": 6000.00, "desc": "Modern loft in the city center", "capacity": 2},
            {"name": "Lamu Island Retreat", "location": "Lamu", "coords": kenyan_locations["Lamu"], "price": 15000.00, "desc": "Traditional Swahili-style house", "capacity": 4},
            {"name": "Eldoret Farmhouse", "location": "Eldoret", "coords": kenyan_locations["Eldoret"], "price": 7000.00, "desc": "Rustic farmhouse with gardens", "capacity": 6},
            {"name": "Nyeri Hill Cabin", "location": "Nyeri", "coords": kenyan_locations["Nyeri"], "price": 8000.00, "desc": "Cabin with Aberdare views", "capacity": 3},
            {"name": "Nakuru Eco-Lodge", "location": "Nakuru", "coords": kenyan_locations["Nakuru"], "price": 11000.00, "desc": "Eco-friendly lodge near Lake Nakuru", "capacity": 5},
            {"name": "Nairobi Urban Studio", "location": "Nairobi", "coords": kenyan_locations["Nairobi"], "price": 6500.00, "desc": "Compact studio in Kilimani", "capacity": 2},
            {"name": "Malindi Oceanfront", "location": "Malindi", "coords": kenyan_locations["Malindi"], "price": 13000.00, "desc": "Spacious villa by the sea", "capacity": 7},
            {"name": "Amboseli Safari Camp", "location": "Amboseli", "coords": kenyan_locations["Amboseli"], "price": 18000.00, "desc": "Camp with Kilimanjaro views", "capacity": 6},
            {"name": "Watamu Beach House", "location": "Watamu", "coords": kenyan_locations["Watamu"], "price": 9000.00, "desc": "Charming house near coral reefs", "capacity": 4},
            {"name": "Nanyuki Ranch House", "location": "Nanyuki", "coords": kenyan_locations["Nanyuki"], "price": 10000.00, "desc": "Ranch-style home near Mt. Kenya", "capacity": 5},
            {"name": "Kisii Hills Cottage", "location": "Kisii", "coords": kenyan_locations["Kisii"], "price": 5500.00, "desc": "Quiet cottage in the hills", "capacity": 3},
            {"name": "Thika Modern Villa", "location": "Thika", "coords": kenyan_locations["Thika"], "price": 8500.00, "desc": "Villa with modern amenities", "capacity": 6},
            {"name": "Machakos Retreat", "location": "Machakos", "coords": kenyan_locations["Machakos"], "price": 7000.00, "desc": "Secluded retreat with views", "capacity": 4},
            {"name": "Kericho Tea Farmhouse", "location": "Kericho", "coords": kenyan_locations["Kericho"], "price": 7500.00, "desc": "Farmhouse amidst tea plantations", "capacity": 5},
            {"name": "Voi Safari Lodge", "location": "Voi", "coords": kenyan_locations["Voi"], "price": 12000.00, "desc": "Lodge near Tsavo National Park", "capacity": 6}
        ]

        # Generate additional listing entries
        property_types = ["Apartment", "Villa", "Lodge", "Cottage", "House", "Loft", "Retreat", "Cabin", "Farmhouse", "Camp"]
        for i in range(20, num_listings):
            location = random.choice(list(kenyan_locations.keys()))
            property_type = random.choice(property_types)
            listing_data.append({
                "name": f"{location} {property_type} {i+1}",
                "location": location,
                "coords": kenyan_locations[location],
                "price": round(random.uniform(5000, 20000), 2),
                "desc": fake.sentence(nb_words=10),
                "capacity": random.randint(1, 10)
            })

        for i, data in enumerate(listing_data):
            listing = Listing.objects.create(
                property_id=uuid.uuid4(),
                host=hosts[i % len(hosts)],
                name=data["name"],
                description=data["desc"],
                location=data["location"],
                price_per_night=data["price"],
                created_at=timezone.make_aware(datetime(2025, 2, 1, 0, 0, 0) + timedelta(days=i)),
                updated_at=timezone.make_aware(datetime(2025, 2, 1, 0, 0, 0) + timedelta(days=i)),
                property_images=f"property_images/listing{i+1}.jpg" if random.choice([True, False]) else None,
                capacity=data["capacity"],
                amenities=random.choice(amenities_options),
                availability={}
            )
            listings.append(listing)

        # Create Booking entries
        guests = [u for u in users if u.user_role == "guest"]
        bookings = []
        booking_data = [
            {"start_date": timezone.make_aware(datetime(2025, 3, 1, 0, 0, 0)), "end_date": timezone.make_aware(datetime(2025, 3, 5, 0, 0, 0)), "status": "PENDING"},
            {"start_date": timezone.make_aware(datetime(2025, 3, 6, 0, 0, 0)), "end_date": timezone.make_aware(datetime(2025, 3, 10, 0, 0, 0)), "status": "CONFIRMED"},
            {"start_date": timezone.make_aware(datetime(2025, 3, 11, 0, 0, 0)), "end_date": timezone.make_aware(datetime(2025, 3, 14, 0, 0, 0)), "status": "CANCELLED"},
            {"start_date": timezone.make_aware(datetime(2025, 3, 15, 0, 0, 0)), "end_date": timezone.make_aware(datetime(2025, 3, 19, 0, 0, 0)), "status": "PENDING"},
            {"start_date": timezone.make_aware(datetime(2025, 3, 20, 0, 0, 0)), "end_date": timezone.make_aware(datetime(2025, 3, 25, 0, 0, 0)), "status": "CONFIRMED"}
        ]

        # Generate additional booking entries with non-overlapping dates
        for i in range(5, num_bookings):
            listing = listings[i % len(listings)]
            start_date = timezone.make_aware(datetime(2025, 3, 1, 0, 0, 0) + timedelta(days=(i % 90)))
            end_date = start_date + timedelta(days=random.randint(2, 7))
            # Check for overlaps
            overlapping = Booking.objects.filter(
                listing=listing,
                end_date__gt=start_date,
                start_date__lt=end_date,
                booking_status__in=['PENDING', 'CONFIRMED']
            ).exists()
            if not overlapping:
                booking_data.append({
                    "start_date": start_date,
                    "end_date": end_date,
                    "status": random.choice(["PENDING", "CONFIRMED", "CANCELLED"])
                })

        for i, data in enumerate(booking_data):
            listing = listings[i % len(listings)]
            booking = Booking.objects.create(
                booking_id=uuid.uuid4(),
                listing=listing,
                user=guests[i % len(guests)],
                start_date=data["start_date"],
                end_date=data["end_date"],
                booking_status=data["status"],
                created_at=data["start_date"]
            )
            # Update listing availability
            current_availability = listing.availability
            for d in range((data["end_date"] - data["start_date"]).days):
                date_str = (data["start_date"] + timedelta(days=d)).strftime('%Y-%m-%d')
                current_availability[date_str] = data["status"] != "CANCELLED"
            listing.availability = current_availability
            listing.save()
            bookings.append(booking)

        # Create Payment entries
        payment_data = [
            {"method": "CREDIT CARD", "status": "COMPLETED", "date": timezone.make_aware(datetime(2025, 3, i + 1, 0, 0, 0)), "tx_id": f"TX{i+1:06d}"} for i in range(5)
        ] + [
            {"method": "PAYPAL", "status": "PENDING", "date": timezone.make_aware(datetime(2025, 3, i + 6, 0, 0, 0)), "tx_id": f"TX{i+6:06d}"} for i in range(5)
        ] + [
            {"method": "MOBILE MONEY", "status": "COMPLETED", "date": timezone.make_aware(datetime(2025, 3, i + 11, 0, 0, 0)), "tx_id": f"TX{i+11:06d}"} for i in range(5)
        ] + [
            {"method": "STRIPE", "status": "FAILED", "date": timezone.make_aware(datetime(2025, 3, i + 16, 0, 0, 0)), "tx_id": f"TX{i+16:06d}"} for i in range(5)
        ]

        payment_methods = ["CREDIT CARD", "PAYPAL", "MOBILE MONEY", "STRIPE"]
        payment_statuses = ["PENDING", "COMPLETED", "FAILED", "REFUNDED"]
        for i in range(20, num_payments):
            payment_data.append({
                "method": random.choice(payment_methods),
                "status": random.choice(payment_statuses),
                "date": timezone.make_aware(datetime(2025, 3, (i % 30) + 1, 0, 0, 0)),
                "tx_id": f"TX{i+1:06d}"
            })

        payment_count = 0
        for i, data in enumerate(payment_data):
            if payment_count >= num_payments:
                break
            booking = bookings[i % len(bookings)]
            if booking.booking_status != "CANCELLED":
                payment = Payment.objects.create(
                    payment_id=uuid.uuid4(),
                    booking_id=booking,
                    amount=booking.get_total_price,
                    payment_date=data["date"],
                    payment_method=data["method"],
                    payment_status=data["status"],
                    transaction_id=data["tx_id"],
                    user=booking.user
                )
                booking.booking_payment = payment
                booking.save()
                payment_count += 1

        # Create Review entries
        review_data = [
            {"rating": 4, "comment": "Great stay, very comfortable!", "date": timezone.make_aware(datetime(2025, 4, 1, 0, 0, 0)), "approved": True},
            {"rating": 5, "comment": "Amazing views and hospitality", "date": timezone.make_aware(datetime(2025, 4, 2, 0, 0, 0)), "approved": True},
            {"rating": 3, "comment": None, "date": timezone.make_aware(datetime(2025, 4, 3, 0, 0, 0)), "approved": False},
            {"rating": 4, "comment": "Clean and cozy place", "date": timezone.make_aware(datetime(2025, 4, 4, 0, 0, 0)), "approved": True},
            {"rating": 5, "comment": "Perfect for a getaway", "date": timezone.make_aware(datetime(2025, 4, 5, 0, 0, 0)), "approved": True}
        ]

        for i in range(5, num_reviews):
            review_data.append({
                "rating": random.randint(1, 5),
                "comment": fake.sentence(nb_words=10) if random.choice([True, False]) else None,
                "date": timezone.make_aware(datetime(2025, 4, (i % 30) + 1, 0, 0, 0)),
                "approved": random.choice([True, False])
            })

        review_count = 0
        for i, data in enumerate(review_data):
            if review_count >= num_reviews:
                break
            booking = bookings[i % len(bookings)]
            if booking.booking_status == "CONFIRMED":
                review = Review.objects.create(
                    review_id=uuid.uuid4(),
                    user=guests[i % len(guests)],
                    booking=booking,
                    listing=booking.listing,
                    review_date=data["date"],
                    review_rating=data["rating"],
                    comment=data["comment"],
                    is_approved=data["approved"]
                )
                review_count += 1

        # Create Message entries
        message_data = [
            {"title": "Booking Inquiry", "body": "Is your property available next week?", "date": timezone.make_aware(datetime(2025, 5, 1, 0, 0, 0)), "read": False},
            {"title": "Check-in Details", "body": "Please provide check-in instructions.", "date": timezone.make_aware(datetime(2025, 5, 2, 0, 0, 0)), "read": True},
            {"title": "Property Questions", "body": "Does the villa have Wi-Fi?", "date": timezone.make_aware(datetime(2025, 5, 3, 0, 0, 0)), "read": False},
            {"title": "Reservation Request", "body": "Can you reserve for 3 nights?", "date": timezone.make_aware(datetime(2025, 5, 4, 0, 0, 0)), "read": True},
            {"title": "Amenities Info", "body": "Is there a pool at the lodge?", "date": timezone.make_aware(datetime(2025, 5, 5, 0, 0, 0)), "read": False}
        ]

        for i in range(5, num_messages):
            message_data.append({
                "title": fake.sentence(nb_words=3)[:30],
                "body": fake.paragraph()[:1000],
                "date": timezone.make_aware(datetime(2025, 5, (i % 30) + 1, 0, 0, 0)),
                "read": random.choice([True, False])
            })

        for i, data in enumerate(message_data):
            sender = users[i % len(users)]
            recipient = random.choice([u for u in users if u != sender])  # Prevent self-messaging
            message = Message.objects.create(
                message_id=uuid.uuid4(),
                sender=sender,
                recipient=recipient,
                sent_at=data["date"],
                message_title=data["title"],
                message_body=data["body"],
                is_read=data["read"]
            )

        self.stdout.write(self.style.SUCCESS(
            f"Database seeded with {len(user_data)} users, {len(listing_data)} listings, "
            f"{len(bookings)} bookings, {payment_count} payments, {review_count} reviews, "
            f"and {len(message_data)} messages."
        ))