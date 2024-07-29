from django.db import models

# Create your models here.
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
