from django.utils import timezone
from rest_framework import serializers
from .models import Booking, Guest, Invoice, Room

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking        
        exclude = ['total_price'] # Still exclude total_price
    
    def validate(self, data):
        # Check that check-out is after check-in
        if data['check_in_date'] >= data['check_out_date']:
            raise serializers.ValidationError("Check-out date must be after \
                                              check-in date.")

        # Check that check-in is not in the past
        if data['check_in_date'] < timezone.now().date():
            raise serializers.ValidationError("Check-in date cannot be in the \
                                              past.")
        
        # Check that payment_method is not None
        if not data['payment_method']:
            raise serializers.ValidationError("Payment method is required.")

        return data

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
