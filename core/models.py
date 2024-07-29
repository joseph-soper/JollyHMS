from django.db import models

# Create your models here.
class Guest(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True) # Allow blank addresses

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Room(models.Model):
    ROOM_TYPES = (
        ('Q', 'Single Queen'),
        ('K', 'Single King'),
        ('QD', 'Double Queen'),
        ('KD', 'Double King'),
        ('QS', 'Queen Suite'),
        ('KS', 'King Suite'),
    )
    number = models.CharField(max_length=5, unique=True)
    room_type = models.CharField(max_length=2, choices=ROOM_TYPES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.number} ({self.room_type})"

class Booking(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Booking for {self.guest.first_name} in Room {self.room.number}"
    
class Invoice(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=(
        ('credit_card', 'Credit Card'),
        ('cash', 'Cash'),
    ))
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice for Booking {self.booking.id}"
