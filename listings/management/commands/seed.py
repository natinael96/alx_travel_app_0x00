"""
Management command to seed the database with sample listings data.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random
from listings.models import Listing, Booking, Review


class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--listings',
            type=int,
            default=20,
            help='Number of listings to create (default: 20)',
        )
        parser.add_argument(
            '--bookings',
            type=int,
            default=50,
            help='Number of bookings to create (default: 50)',
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=100,
            help='Number of reviews to create (default: 100)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        num_listings = options['listings']
        num_bookings = options['bookings']
        num_reviews = options['reviews']
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        
        # Create listings
        self.stdout.write(self.style.SUCCESS(f'Creating {num_listings} listings...'))
        listings = self.create_listings(num_listings)
        
        # Create bookings
        self.stdout.write(self.style.SUCCESS(f'Creating {num_bookings} bookings...'))
        self.create_bookings(listings, num_bookings)
        
        # Create reviews
        self.stdout.write(self.style.SUCCESS(f'Creating {num_reviews} reviews...'))
        self.create_reviews(listings, num_reviews)
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Created: {Listing.objects.count()} listings, '
                                            f'{Booking.objects.count()} bookings, '
                                            f'{Review.objects.count()} reviews'))

    def create_listings(self, count):
        """Create sample listings."""
        neighborhoods = [
            'Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island',
            'Downtown', 'Midtown', 'Uptown', 'East Side', 'West Side',
            'Greenwich Village', 'SoHo', 'Chelsea', 'Upper East Side', 'Upper West Side'
        ]
        
        room_types = ['entire_home', 'private_room', 'shared_room']
        
        host_names = [
            'John Smith', 'Sarah Johnson', 'Michael Brown', 'Emily Davis', 'David Wilson',
            'Jessica Martinez', 'Christopher Anderson', 'Amanda Taylor', 'Matthew Thomas',
            'Lauren Jackson', 'Daniel White', 'Michelle Harris', 'James Martin', 'Ashley Thompson'
        ]
        
        titles = [
            'Cozy Apartment in the Heart of the City',
            'Beautiful Studio with Amazing Views',
            'Spacious 2BR Apartment Near Subway',
            'Modern Loft in Trendy Neighborhood',
            'Charming House with Garden',
            'Luxury Penthouse with Rooftop Access',
            'Quiet Room in Friendly Neighborhood',
            'Stylish Condo with Modern Amenities',
            'Historic Brownstone Apartment',
            'Bright and Airy Downtown Loft',
            'Comfortable Home Away from Home',
            'Elegant Apartment with City Views',
            'Cozy Studio Perfect for Solo Travelers',
            'Family-Friendly 3BR House',
            'Boutique Apartment in Prime Location'
        ]
        
        descriptions = [
            'A beautiful and comfortable space perfect for your stay. Located in a prime area with easy access to public transportation and local attractions.',
            'This stunning property offers modern amenities and a convenient location. Perfect for business travelers and tourists alike.',
            'Experience the best of city living in this well-appointed accommodation. Close to restaurants, shops, and entertainment.',
            'A peaceful retreat in the heart of the city. This property combines comfort and convenience for an unforgettable stay.',
            'Modern design meets comfort in this exceptional space. Ideal for couples, families, or solo travelers seeking a memorable experience.'
        ]
        
        listings = []
        for i in range(count):
            host_id = f'HOST{1000 + i}'
            room_type = random.choice(room_types)
            
            listing = Listing.objects.create(
                title=random.choice(titles),
                description=random.choice(descriptions),
                host_name=random.choice(host_names),
                host_id=host_id,
                neighborhood=random.choice(neighborhoods),
                latitude=Decimal(str(round(random.uniform(40.5, 40.9), 6))),
                longitude=Decimal(str(round(random.uniform(-74.0, -73.7), 6))),
                room_type=room_type,
                accommodates=random.randint(1, 6),
                bedrooms=random.randint(1, 4) if room_type == 'entire_home' else random.randint(1, 2),
                beds=random.randint(1, 4),
                bathrooms=Decimal(str(round(random.uniform(1.0, 3.0), 1))),
                price=Decimal(str(round(random.uniform(50, 500), 2))),
                minimum_nights=random.randint(1, 7),
                availability_365=random.randint(0, 365),
            )
            listings.append(listing)
            
            if (i + 1) % 5 == 0:
                self.stdout.write(f'  Created {i + 1}/{count} listings...')
        
        return listings

    def create_bookings(self, listings, count):
        """Create sample bookings."""
        guest_names = [
            'Alice Cooper', 'Bob Dylan', 'Charlie Brown', 'Diana Prince', 'Edward Norton',
            'Fiona Apple', 'George Clooney', 'Helen Mirren', 'Ian McKellen', 'Julia Roberts',
            'Kevin Spacey', 'Lena Headey', 'Mark Ruffalo', 'Natalie Portman', 'Oscar Isaac'
        ]
        
        statuses = ['pending', 'confirmed', 'completed', 'cancelled']
        status_weights = [0.1, 0.3, 0.5, 0.1]  # More completed bookings
        
        today = timezone.now().date()
        
        for i in range(count):
            listing = random.choice(listings)
            
            # Generate check-in date (past or future)
            days_offset = random.randint(-180, 180)
            check_in = today + timedelta(days=days_offset)
            
            # Generate check-out date (1 to 14 nights after check-in)
            nights = random.randint(1, 14)
            # Ensure minimum nights requirement
            if nights < listing.minimum_nights:
                nights = listing.minimum_nights
            check_out = check_in + timedelta(days=nights)
            
            # Choose status based on dates
            if check_out < today:
                status = 'completed'
            elif check_in > today:
                status = random.choices(statuses, weights=status_weights)[0]
            else:
                status = random.choice(['confirmed', 'completed'])
            
            price_per_night = listing.price
            total_price = price_per_night * nights
            
            Booking.objects.create(
                listing=listing,
                guest_name=random.choice(guest_names),
                guest_email=f'guest{i}@example.com',
                guest_phone=f'+1-555-{random.randint(1000, 9999)}',
                check_in=check_in,
                check_out=check_out,
                guests=random.randint(1, listing.accommodates),
                price_per_night=price_per_night,
                total_price=total_price,
                status=status,
                special_requests=random.choice([
                    '', 
                    'Late check-in requested',
                    'Need extra towels',
                    'Quiet room preferred',
                    'Early check-in if possible'
                ]) if random.random() > 0.7 else '',
            )
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Created {i + 1}/{count} bookings...')

    def create_reviews(self, listings, count):
        """Create sample reviews."""
        reviewer_names = [
            'Alex Turner', 'Blake Lively', 'Chris Evans', 'Dakota Johnson', 'Emma Stone',
            'Felicity Jones', 'Gareth Bale', 'Hugh Jackman', 'Isla Fisher', 'Jake Gyllenhaal',
            'Kate Winslet', 'Liam Neeson', 'Margot Robbie', 'Noah Centineo', 'Olivia Wilde'
        ]
        
        comments_templates = [
            'Great place to stay! Very clean and comfortable.',
            'Amazing location and wonderful host. Highly recommend!',
            'Perfect for our needs. Would definitely stay again.',
            'Beautiful property with all the amenities we needed.',
            'The host was very responsive and helpful throughout our stay.',
            'Lovely space, exactly as described. Great value for money.',
            'Excellent experience! The place was spotless and well-maintained.',
            'Convenient location with easy access to public transport.',
            'Comfortable and cozy. Perfect for a weekend getaway.',
            'Outstanding hospitality and a wonderful place to relax.',
            'The property exceeded our expectations. Highly satisfied!',
            'Clean, modern, and in a great neighborhood.',
            'Fantastic stay! Everything was perfect.',
            'Great communication from the host. Smooth check-in process.',
            'Would love to come back! Great experience overall.'
        ]
        
        for i in range(count):
            listing = random.choice(listings)
            rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.1, 0.15, 0.3, 0.4])[0]
            
            review = Review.objects.create(
                listing=listing,
                reviewer_name=random.choice(reviewer_names),
                reviewer_id=f'REV{random.randint(10000, 99999)}',
                comments=random.choice(comments_templates),
                rating=rating,
                accuracy_rating=random.randint(1, 5) if random.random() > 0.3 else None,
                cleanliness_rating=random.randint(1, 5) if random.random() > 0.3 else None,
                checkin_rating=random.randint(1, 5) if random.random() > 0.3 else None,
                communication_rating=random.randint(1, 5) if random.random() > 0.3 else None,
                location_rating=random.randint(1, 5) if random.random() > 0.3 else None,
                value_rating=random.randint(1, 5) if random.random() > 0.3 else None,
            )
            
            if (i + 1) % 20 == 0:
                self.stdout.write(f'  Created {i + 1}/{count} reviews...')

