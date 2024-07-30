from django.contrib import admin
from .models import Booking, Guest, Invoice, Room, UserProfile, UserRole

class GuestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'date_of_birth')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('date_of_birth',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')

class BookingAdmin(admin.ModelAdmin):
    list_display = ('guest', 'room', 'check_in_date', 'check_out_date', 'total_price', 'is_active', 'payment_method')
    search_fields = ('guest__first_name', 'guest__last_name', 'room__number')
    list_filter = ('check_in_date', 'check_out_date', 'is_active')
    

    def has_view_or_change_permission(self, request, obj=None):
        # Allow all staff members to view bookings
        return request.user.is_staff
    
    def has_add_permission(self, request):
        # Allow only managers and admins to add bookings
        return request.user.userprofile.role.name in ['Manager', 'Admin']
    
    def has_delete_permission(self, request, obj=None):
        # Allow only admins to delete bookings
        return request.user.userprofile.role.name == 'Admin'

# Register your models here.
admin.site.register(Booking, BookingAdmin)
admin.site.register(Guest, GuestAdmin)
admin.site.register(UserRole)
admin.site.register(UserProfile, UserProfileAdmin)
