from collections import Counter
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Count, Q
from django.shortcuts import render
from .permissions import IsGuest, IsStaff, IsAdmin, IsManager
from rest_framework import status, generics, permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import stripe
from .models import Booking, Guest, Invoice, Room, UserRole, UserProfile
from .serializers import BookingSerializer, GuestSerializer, \
    InvoiceSerializer, RoomSerializer, UserSerializer

# Create your views here.
###############################################################################################################
###############################################################################################################
######################################## Class Based Views #################################################
###############################################################################################################
###############################################################################################################

class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

    permission_classes = [IsGuest]

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    permission_classes = [IsStaff]

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    permission_classes = [IsAuthenticated]

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

    @action(detail=True, methods=['POST'])
    def check_in(self, request, pk=None):
        booking = self.get_object()

        if not booking.is_active:  # Check if booking is active
            return Response({"error": "Booking is not active."},
            status=status.HTTP_400_BAD_REQUEST)
        if booking.check_in_date != date.today(): # Verify they are checking in today
            return Response({"error": "Cannot check in on a different date."},
            status=status.HTTP_400_BAD_REQUEST)
        
        booking.is_active = False
        booking.room.is_available = False
        booking.save()
        booking.room.save()

        return Response({"message": "Check-in successful"})
    
    @action(detail=True, methods=['POST'])
    def check_out(self, request, pk=None):
        booking = self.get_object()

        if not booking.is_active:  # Check if booking is active
            return Response({"error": "Booking is not active."},
            status=status.HTTP_400_BAD_REQUEST)
        
        booking.room.is_available = True
        booking.room.save()

        # Create an invoice
        create_invoice(booking)

        return Response({"message": "Check-out successful"})

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    permission_classes = [IsGuest]

# Registration View Function
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = serializer.save()
            role = UserRole.objects.get(name='Guest')
            UserProfile.objects.create(user=user, role=role)

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        
        except IntegrityError as e: # Catch potential integrity errors (e.g. duplicate usernames)
            return Response({'error': 'Username or email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

###############################################################################################################
###############################################################################################################
######################################## Function Based Views #################################################
###############################################################################################################
###############################################################################################################

# Create Invoice Function
def create_invoice(booking):
    total_price = booking.total_price
    Invoice.objects.create(
        booking=booking,
        amount=total_price,
        payment_method=booking.payment_method, # Add payment method
    )

# Calculate Revenue Function
@api_view(['GET'])
def calculate_revenue(request):
    # Get start and end dates from query parameters
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')

    # Validate dates
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format. Please use YYYY-MM-DD format.'}, 
                        status=status.HTTP_400_BAD_REQUEST )
    
    # Calculate revenue
    bookings = Booking.objects.filter(
        check_in_date__lte=end_date,
        check_out_date__gte=start_date,
        invoice__is_paid=True, # Ensure only paid bookings are included
    )

    total_revenue = sum(booking.total_price for booking in bookings)

    return Response({'total_revenue': total_revenue})

# Guest Demographics Report Function
@api_view(['GET'])
@permission_classes([IsStaff])
def guest_demographics_report(request):
    # Get all guests
    guests = Guest.objects.all()

    # Calculate demographics
    countries = Counter(guest.address.split(',')[-1].strip() for guest in guests
                        if guest.address) # Extract country from address (assume last part of address is country)
    ages = Counter((date.today().year - guest.date_of_birth.year) for guest in guests 
                   if guest.date_of_birth) #Assuming you have date_of_birth field
    
    return Response({
        'countries': countries,
        'ages': ages
    })

# Login View Function
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # Check user credentials against built in user model
    user = authenticate(request, username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# Occupancy Rate Report Function
@api_view(['GET'])
@permission_classes([IsStaff])
def occupancy_rate_report(request):
    date_str = request.query_params.get('date')

    # Validate date
    try:
        report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Get total rooms and occupied rooms for the given date
    total_rooms = Room.objects.count()
    occupied_rooms = Booking.objects.filter(
        check_in_date__lte=report_date,
        check_out_date__gt=report_date,
        is_active=True
    ).count()

    # Calculate occupancy rate
    occupancy_rate = (occupied_rooms / total_rooms) * 100 if total_rooms > 0 else 0

    return Response({'date': report_date, 'occupancy_rate': occupancy_rate})

# Search Available Rooms Function
@api_view(['GET'])
def search_available_rooms(request):
    check_in_date = request.query_params.get('check_in_date')
    check_out_date = request.query_params.get('check_out_date')
    room_type = request.query_params.get('room_type')

    # Basic validation
    if not check_in_date or not check_out_date:
        return Response({"error": "Please provide check-in and check-out dates."}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    try:
        check_in_date = date.fromisoformat(check_in_date)
        check_out_date = date.fromisoformat(check_out_date)
    except ValueError:
        return Response({"error": "Invalid date format. Please use YYYY-MM-DD format."}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    # Query for available rooms
    available_rooms = Room.objects.filter(is_available=True).exclude(
        bookings__check_in_date__lte=check_out_date, 
        bookings__check_out_date__gte=check_in_date
    )

    if room_type:
        available_rooms = available_rooms.filter(room_type=room_type)

    serializer = RoomSerializer(available_rooms, many=True)
    return Response(serializer.data)

##### Stripe ############################################################################
stripe.api_key = settings.STRIPE_SECRET_KEY

##### Create Payment Intent  #####
@api_view(['POST'])
def create_payment_intent(request):
    try:
        amount = int(request.data['amount'])

        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            automatic_payment_methods={
                'enabled': True,
            },
        )

        return Response({'clientSecret': payment_intent['client_secret']})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

##### Create User #######################################################################
class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        # Create a UserProfile for the new user and assign the default role 'Guest'
        role = UserRole.objects.get(name='Guest')
        UserProfile.objects.create(user=user, role=role)