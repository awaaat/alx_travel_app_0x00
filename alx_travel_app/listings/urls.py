from django.urls import path, include
from . import views
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter

# Base routers
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'property', views.ListingViewSet)
router.register(r'bookings', views.BookingViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'reviews', views.ReviewViewSet)
router.register(r'messages', views.MessageViewSet)

# Nest under user
user_router = NestedDefaultRouter(router, r'users', lookup='user')
user_router.register(r'bookings', views.BookingViewSet, basename='user-bookings')
user_router.register(r'reviews', views.ReviewViewSet, basename='user-reviews')
user_router.register(r'messages', views.MessageViewSet, basename='user-messages')
user_router.register(r'payments', views.PaymentViewSet, basename='user-payments')
user_router.register(r'listings', views.ListingViewSet, basename='user-listings')

# Nest under listing
property_router = NestedDefaultRouter(router, r'property', lookup='property')
property_router.register(r'bookings', views.BookingViewSet, basename='property-bookings')
property_router.register(r'reviews', views.ReviewViewSet, basename='property-reviews')
property_router.register(r'messages', views.MessageViewSet, basename='property-messages')
property_router.register(r'payments', views.PaymentViewSet, basename='property-payments')
property_router.register(r'users', views.UserViewSet, basename='property-users')

# Nest under booking
booking_router = NestedDefaultRouter(router, r'bookings', lookup='booking')
booking_router.register(r'payments', views.PaymentViewSet, basename='booking-payments')
booking_router.register(r'reviews', views.ReviewViewSet, basename='booking-reviews')

# Nest under payment
payment_router = NestedDefaultRouter(router, r'payments', lookup='payment')
payment_router.register(r'booking', views.BookingViewSet, basename='payment-booking')
payment_router.register(r'user', views.UserViewSet, basename='payment-user')

# Nest under message
message_router = NestedDefaultRouter(router, r'messages', lookup='message')
message_router.register(r'sender', views.UserViewSet, basename='message-sender')
message_router.register(r'recipient', views.UserViewSet, basename='message-recipient')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(user_router.urls)),
    path('', include(property_router.urls)),
    path('', include(booking_router.urls)),
    path('', include(payment_router.urls)),
    path('', include(message_router.urls)),
]
