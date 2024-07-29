from django.shortcuts import render
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.response import Response
from datetime import date
from .models import Booking, Guest, Invoice, Room
from .serializers import BookingSerializer, GuestSerializer, \
    InvoiceSerializer, RoomSerializer

# Create your views here.
class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get data from the validated serializer
        room = serializer.validated_data["room"]
        check_in_date = serializer.validated_data["check_in_date"]
        check_out_date = serializer.validated_data["check_out_date"]


        # Basic validations
        if check_in_date >= check_out_date:
            return Response({"error": "Check-out date must be after check-in date."}, status=status.HTTP_400_BAD_REQUEST)
        if check_in_date < date.today():
            return Response({"error": "Check-in date cannot be in the past."}, status=status.HTTP_400_BAD_REQUEST)

        # Overlapping bookings check (Revised Logic)
        overlapping_bookings = Booking.objects.filter(
            room=room,
            is_active=True,
        ).filter(
            Q(check_in_date__range=(check_in_date, check_out_date)) |  # New booking starts within an existing booking
            Q(check_out_date__range=(check_in_date, check_out_date)) |  # New booking ends within an existing booking
            Q(check_in_date__lte=check_in_date, check_out_date__gte=check_out_date)  # New booking encompasses an existing booking
        )

        if overlapping_bookings.exists():
            return Response({"error": "Room is already booked for this period."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price
        num_nights = (check_out_date - check_in_date).days
        total_price = num_nights * room.price
        serializer.validated_data["total_price"] = total_price

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
