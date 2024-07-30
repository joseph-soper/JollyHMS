from django.contrib.auth.models import User
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

    def validate_date_of_birth(self, value):
        # Check if date_of_birth is in the future
        if value > timezone.now().date():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        
        # Check minimum age
        min_age = 18
        today = timezone.now().date()
        if today.year - value.year - ((today.month, today.day) < (value.month, value.day)) < min_age:
            raise serializers.ValidationError(f"Guest must be at least {min_age} years old.")
        
        return value
    
    def validate_email(self, value):
        # Check for valid email format 
        if not "@" in value:
            raise serializers.ValidationError("Invalid email address.")
        
        return value

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'assword', 'email')

        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user
