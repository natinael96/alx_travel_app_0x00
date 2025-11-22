from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Listing(models.Model):
    """
    Model representing a travel accommodation listing.
    """
    ROOM_TYPE_CHOICES = [
        ('entire_home', 'Entire Home/Apt'),
        ('private_room', 'Private Room'),
        ('shared_room', 'Shared Room'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    host_name = models.CharField(max_length=100)
    host_id = models.CharField(max_length=50, unique=True)
    
    # Location
    neighborhood = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Property Details
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    accommodates = models.PositiveIntegerField(default=1)
    bedrooms = models.PositiveIntegerField(default=1)
    beds = models.PositiveIntegerField(default=1)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_nights = models.PositiveIntegerField(default=1)
    
    # Availability
    availability_365 = models.PositiveIntegerField(default=0)
    
    # Ratings (calculated from reviews)
    number_of_reviews = models.PositiveIntegerField(default=0)
    review_scores_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['host_id']),
            models.Index(fields=['neighborhood']),
            models.Index(fields=['room_type']),
            models.Index(fields=['price']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.host_name}"


class Booking(models.Model):
    """
    Model representing a booking/reservation for a listing.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    listing = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    
    # Guest Information
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20, blank=True)
    
    # Booking Details
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    
    # Pricing
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Special Requests
    special_requests = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', 'check_in', 'check_out']),
            models.Index(fields=['status']),
            models.Index(fields=['guest_email']),
        ]
    
    def __str__(self):
        return f"Booking {self.id} - {self.listing.title} ({self.check_in} to {self.check_out})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.check_out <= self.check_in:
            raise ValidationError("Check-out date must be after check-in date.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Review(models.Model):
    """
    Model representing a review/rating for a listing.
    """
    listing = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    
    # Reviewer Information
    reviewer_name = models.CharField(max_length=100)
    reviewer_id = models.CharField(max_length=50, blank=True)
    
    # Review Content
    comments = models.TextField()
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    
    # Detailed Ratings (optional)
    accuracy_rating = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    cleanliness_rating = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    checkin_rating = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    communication_rating = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    location_rating = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    value_rating = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', 'rating']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Review by {self.reviewer_name} for {self.listing.title} - {self.rating}/5"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update listing's review count and average rating
        self.update_listing_ratings()
    
    def delete(self, *args, **kwargs):
        listing = self.listing
        super().delete(*args, **kwargs)
        # Update listing's review count and average rating after deletion
        self._update_listing_ratings(listing)
    
    def update_listing_ratings(self):
        """Update the listing's review count and average rating."""
        self._update_listing_ratings(self.listing)
    
    @staticmethod
    def _update_listing_ratings(listing):
        """Helper method to update listing ratings."""
        reviews = Review.objects.filter(listing=listing)
        listing.number_of_reviews = reviews.count()
        if listing.number_of_reviews > 0:
            avg_rating = reviews.aggregate(
                avg=models.Avg('rating')
            )['avg']
            listing.review_scores_rating = round(avg_rating, 2) if avg_rating else None
        else:
            listing.review_scores_rating = None
        listing.save(update_fields=['number_of_reviews', 'review_scores_rating'])

