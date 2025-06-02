from django.urls import path, include
from . import views
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'property', views.ListingViewSet)
router.register(r'booking', views.BookingViewSet)
router.register(r'payment', views.PaymentViewSet)
router.register(r'reviews', views.ReviewViewSet)
router.register(r'message', views.MessageViewSet)

# Nested routers
user_router = NestedDefaultRouter(router, r'user', lookup='user')
user_router.register(r'bookings', views.BookingViewSet, basename='user-bookings')
user_router.register(r'reviews', views.ReviewViewSet, basename='user-reviews')
user_router.register(r'messages', views.MessageViewSet, basename='user-messages')

property_router = NestedDefaultRouter(router, r'property', lookup='property')
property_router.register(r'bookings', views.BookingViewSet, basename='property-bookings')
property_router.register(r'reviews', views.ReviewViewSet, basename='property-reviews')
property_router.register(r'messages', views.MessageViewSet, basename='property-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(user_router.urls)),
    path('', include(property_router.urls)),
    path('', views.index, name='index'),
]