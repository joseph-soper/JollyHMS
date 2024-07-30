from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from core.models import Booking, Room
from datetime import date

# Create your views here.
@login_required
@permission_required('core.view_booking')
def bookings(request):
    # Setup fetch and pass booking data later
    return render(request, 'dashboard/bookings.html')

@login_required
@permission_required('core.view_booking')
def overview(request):  # Make sure the function is defined
    today = date.today()
    arrivals_today = Booking.objects.filter(check_in_date=today).count()
    departures_today = Booking.objects.filter(check_out_date=today).count()

    occupied_rooms = Room.objects.filter(is_available=False).count()
    total_rooms = Room.objects.count()
    occupancy_rate = (occupied_rooms / total_rooms) * 100 if total_rooms > 0 else 0

    context = {
        'arrivals_today': arrivals_today,
        'departures_today': departures_today,
        'occupancy_rate': occupancy_rate,
    }
    return render(request, 'dashboard/overview.html', context)
