from django.contrib import admin
from .models import Listing, Booking, Review

# Register your models here.
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'host_name', 'neighborhood', 'room_type', 'price', 'minimum_nights', 'created_at')
    list_filter = ('room_type', 'neighborhood', 'created_at')
    search_fields = ('title', 'host_name', 'neighborhood', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('listing', 'guest_name', 'check_in', 'check_out', 'guests', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'check_in', 'check_out', 'created_at')
    search_fields = ('guest_name', 'listing__title', 'listing__host_name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('listing', 'reviewer_name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer_name', 'listing__title', 'comments')
    readonly_fields = ('created_at', 'updated_at')

