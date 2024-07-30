from rest_framework import serializers
from .models import Booking, Guest, Invoice, Room

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        
        exclude = ['total_price'] # Exclude total_price for now

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
