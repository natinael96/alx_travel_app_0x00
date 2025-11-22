# ALX Travel App 0x00

A Django REST Framework application for managing travel listings, bookings, and reviews.

## Features

- **Listings**: Manage accommodation listings with details like location, pricing, and amenities
- **Bookings**: Handle reservations with check-in/check-out dates and guest information
- **Reviews**: Store and manage reviews with ratings for listings

## Project Structure

```
alx_travel_app_0x00/
├── alx_travel_app/          # Main Django project
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL configuration
│   └── ...
├── listings/                # Listings app
│   ├── models.py            # Database models (Listing, Booking, Review)
│   ├── serializers.py       # API serializers
│   ├── admin.py             # Django admin configuration
│   └── management/
│       └── commands/
│           └── seed.py      # Database seeding command
├── manage.py
└── requirements.txt
```

## Models

### Listing
- Accommodation details (title, description, host information)
- Location (neighborhood, coordinates)
- Property details (room type, bedrooms, beds, bathrooms)
- Pricing and availability
- Review statistics

### Booking
- Guest information
- Check-in/check-out dates
- Pricing and status
- Special requests

### Review
- Reviewer information
- Rating (1-5 stars)
- Detailed ratings (accuracy, cleanliness, check-in, communication, location, value)
- Comments

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure database:**
   - Update database settings in `alx_travel_app/settings.py` or use environment variables
   - Create a MySQL database named `alx_travel_db` (or configure as needed)

3. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Seed the database:**
   ```bash
   python manage.py seed
   ```
   
   Optional parameters:
   ```bash
   python manage.py seed --listings 50 --bookings 100 --reviews 200
   ```

## API Serializers

### ListingSerializer
Serializes Listing model with all fields including computed fields like `room_type_display`.

### BookingSerializer
Serializes Booking model with:
- Related listing information
- Calculated fields (nights, status_display)
- Validation for check-in/check-out dates
- Automatic total price calculation

## Management Commands

### seed
Populates the database with sample data:
- `--listings`: Number of listings to create (default: 20)
- `--bookings`: Number of bookings to create (default: 50)
- `--reviews`: Number of reviews to create (default: 100)

## Development

Run the development server:
```bash
python manage.py runserver
```

Access the admin panel at: `http://localhost:8000/admin/`

API documentation (Swagger) at: `http://localhost:8000/swagger/`

## Author

natinael96 (natinael.96@gmail.com)

