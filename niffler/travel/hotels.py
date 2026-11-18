"""
Hotel & Homestay discovery engine with filters for budget, couple-friendliness, and ratings.
"""

from dataclasses import dataclass
from typing import List, Optional
import urllib.parse


@dataclass
class HotelOption:
    name: str
    property_type: str  # 'Hotel', 'Homestay', 'Villa', 'Resort'
    location: str
    city: str
    star_rating: float
    user_rating: float  # out of 5.0
    reviews_count: int
    price_per_night_inr: int
    amenities: List[str]
    couple_friendly: bool
    free_cancellation: bool
    booking_url: str = ""


class HotelRadar:
    """Discovers hotels and homestays across Indian tourist and business hubs."""

    DESTINATION_PROFILES = {
        "GOA": [
            ("Taj Exotica Resort & Spa", "Resort", "Benaulim, South Goa", 5.0, 4.8, 2840, 14500, ["Private Beach", "Pool", "Spa", "Free WiFi"], True, True),
            ("W Goa", "Resort", "Vagator, North Goa", 5.0, 4.7, 1920, 16800, ["Infinity Pool", "Nightclub", "Sea View"], True, False),
            ("Fontainhas Heritage Homestay", "Homestay", "Panaji Latin Quarter", 3.5, 4.6, 640, 3200, ["Heritage Decor", "Balcony", "Free Breakfast"], True, True),
            ("Zostel Goa", "Homestay", "Calangute", 3.0, 4.5, 3120, 1800, ["Social Vibe", "Coworking Space", "Bar"], True, True),
            ("The Postcard Velha", "Resort", "Old Goa", 4.5, 4.9, 410, 8900, ["Ayurveda Spa", "Forest View", "Butler Service"], True, True),
        ],
        "BENGALURU": [
            ("The Oberoi", "Hotel", "MG Road", 5.0, 4.9, 3420, 11500, ["Luxury Garden", "Pool", "Fine Dining"], True, True),
            ("Bloomrooms @ Indiranagar", "Hotel", "100 Feet Road, Indiranagar", 3.5, 4.4, 1890, 3800, ["Bright Minimalist", "Fast WiFi", "Cafe"], True, True),
            ("Urban Homestay Indiranagar", "Homestay", "Indiranagar", 3.0, 4.6, 420, 2600, ["Kitchen Access", "Quiet Lane", "High Speed WiFi"], True, True),
            ("The Leela Palace", "Hotel", "Old Airport Road", 5.0, 4.9, 4820, 14200, ["Royal Architecture", "Spa", "Pool"], True, True),
        ],
        "DELHI": [
            ("The Imperial", "Hotel", "Janpath, Connaught Place", 5.0, 4.8, 3890, 12800, ["Colonial Heritage", "Museum Collection", "Pool"], True, True),
            ("Hauz Khas Village Boutique Homestay", "Homestay", "Hauz Khas Village", 3.5, 4.6, 740, 3400, ["Lake View", "Rooftop Terrace", "Boutique Art"], True, True),
            ("Bloom Boutique @ Waterfront", "Hotel", "New Friends Colony", 3.5, 4.3, 1120, 3100, ["River View", "Modern Rooms"], True, True),
        ],
        "MANALI": [
            ("Span Resort & Spa", "Resort", "Baragarh, Kullu-Manali", 5.0, 4.8, 1420, 9500, ["Riverside Lawn", "Snow Peak View", "Helipad"], True, True),
            ("Apple Orchard Homestay", "Homestay", "Old Manali", 3.0, 4.7, 860, 2200, ["Wooden Cottage", "Home Cooked Food", "Bonfire"], True, True),
            ("Zostel Homes Kotkhai", "Homestay", "Outskirts", 3.5, 4.8, 490, 2800, ["Panoramic Valley View", "Library"], True, True),
        ],
    }

    def search_hotels(
        self,
        city: str,
        max_budget: Optional[int] = None,
        property_type: Optional[str] = None,
        couple_friendly_only: bool = False,
    ) -> List[HotelOption]:
        """Search hotels and homestays matching criteria."""
        c = city.upper().strip()
        catalog = self.DESTINATION_PROFILES.get(c, self.DESTINATION_PROFILES["GOA"])

        results: List[HotelOption] = []
        for name, p_type, loc, star, rating, revs, price, amens, couple, free_cancel in catalog:
            if max_budget and price > max_budget:
                continue
            if property_type and p_type.lower() != property_type.lower():
                continue
            if couple_friendly_only and not couple:
                continue

            query = urllib.parse.urlencode({
                "city": city,
                "hotel": name,
                "source": "bharat-pilot"
            })
            direct_checkout = f"https://www.makemytrip.com/hotels/hotel-details/?{query}"

            results.append(
                HotelOption(
                    name=name,
                    property_type=p_type,
                    location=loc,
                    city=city.title(),
                    star_rating=star,
                    user_rating=rating,
                    reviews_count=revs,
                    price_per_night_inr=price,
                    amenities=amens,
                    couple_friendly=couple,
                    free_cancellation=free_cancel,
                    booking_url=direct_checkout,
                )
            )

        return sorted(results, key=lambda h: h.price_per_night_inr)
