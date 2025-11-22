from rest_framework import serializers
from .models import Listing, Booking, Review


class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for Listing model.
    """
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)
    
    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'description',
            'host_name',
            'host_id',
            'neighborhood',
            'latitude',
            'longitude',
            'room_type',
            'room_type_display',
            'accommodates',
            'bedrooms',
            'beds',
            'bathrooms',
            'price',
            'minimum_nights',
            'availability_365',
            'number_of_reviews',
            'review_scores_rating',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'number_of_reviews', 'review_scores_rating']


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model.
    """
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(),
        source='listing',
        write_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    nights = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id',
            'listing',
            'listing_id',
            'listing_title',
            'guest_name',
            'guest_email',
            'guest_phone',
            'check_in',
            'check_out',
            'guests',
            'nights',
            'price_per_night',
            'total_price',
            'status',
            'status_display',
            'special_requests',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_nights(self, obj):
        """Calculate the number of nights."""
        if obj.check_in and obj.check_out:
            return (obj.check_out - obj.check_in).days
        return None
    
    def validate(self, data):
        """Validate booking data."""
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError({
                    'check_out': 'Check-out date must be after check-in date.'
                })
            
            # Check minimum nights requirement
            listing = data.get('listing')
            if listing:
                nights = (check_out - check_in).days
                if nights < listing.minimum_nights:
                    raise serializers.ValidationError({
                        'check_out': f'Minimum {listing.minimum_nights} nights required for this listing.'
                    })
        
        return data
    
    def create(self, validated_data):
        """Create a new booking and calculate total price."""
        listing = validated_data['listing']
        check_in = validated_data['check_in']
        check_out = validated_data['check_out']
        
        # Calculate number of nights
        nights = (check_out - check_in).days
        
        # Set price per night from listing if not provided
        if 'price_per_night' not in validated_data:
            validated_data['price_per_night'] = listing.price
        
        # Calculate total price
        validated_data['total_price'] = validated_data['price_per_night'] * nights
        
        return super().create(validated_data)

