from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, GuestViewSet, InvoiceViewSet, RoomViewSet, \
    calculate_revenue, search_available_rooms

router = DefaultRouter()
router.register(r'guests', GuestViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'invoices', InvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('calculate-revenue/', calculate_revenue, name='calculate_revenue'),
    path('search-rooms/', search_available_rooms, name='search_available_rooms'),
]
