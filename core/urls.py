from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, GuestViewSet, InvoiceViewSet, RoomViewSet, \
    calculate_revenue, guest_demographics_report, occupancy_rate_report, \
    search_available_rooms

router = DefaultRouter()
router.register(r'guests', GuestViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'invoices', InvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('calculate-revenue/', calculate_revenue, name='calculate_revenue'),
    path('guest-demographics-report/', guest_demographics_report, name='guest_demographics_report'),
    path('occupancy-rate-report/', occupancy_rate_report, name='occupancy_rate_report'),
    path('search-rooms/', search_available_rooms, name='search_available_rooms'),
]
