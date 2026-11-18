"""
Passenger auto-fill and direct payment gateway handoff coordinator.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import uuid
import datetime
import urllib.parse
from ..config import UserProfile


@dataclass
class BookingSession:
    session_id: str
    booking_type: str  # 'flight', 'hotel', 'train', 'bus'
    item_title: str
    amount_inr: int
    taxes_inr: int
    convenience_fee_inr: int
    total_payable_inr: int
    passenger_name: str
    passenger_age: int
    passenger_gender: str
    contact_email: str
    contact_phone: str
    payment_gateway_url: str
    status: str = "READY_FOR_PAYMENT"


class BookingHandoffEngine:
    """Auto-fills passenger manifests and generates secure 1-click payment handoffs."""

    def __init__(self, profile: Optional[UserProfile] = None):
        self.profile = profile or UserProfile()

    def prepare_flight_handoff(
        self,
        airline: str,
        flight_number: str,
        origin: str,
        destination: str,
        fare_inr: int,
        travel_date: Optional[str] = None,
    ) -> BookingSession:
        """Create a prepared flight booking session landing on payment."""
        sess_id = f"BP-FLT-{uuid.uuid4().hex[:8].upper()}"
        taxes = int(fare_inr * 0.12)
        conv_fee = 350
        total = fare_inr + taxes + conv_fee

        params = {
            "session": sess_id,
            "type": "flight",
            "pax": self.profile.full_name,
            "email": self.profile.email,
            "phone": self.profile.phone,
            "flight": flight_number,
            "route": f"{origin}-{destination}",
            "amount": total,
            "gateway": "UPI/Razorpay/NetBanking"
        }
        # In production this leads to direct payment screen
        payment_url = f"https://payment.makemytrip.com/checkout?{urllib.parse.urlencode(params)}"

        return BookingSession(
            session_id=sess_id,
            booking_type="Flight",
            item_title=f"{airline} ({flight_number}) • {origin} &rarr; {destination}",
            amount_inr=fare_inr,
            taxes_inr=taxes,
            convenience_fee_inr=conv_fee,
            total_payable_inr=total,
            passenger_name=self.profile.full_name,
            passenger_age=self.profile.age,
            passenger_gender=self.profile.gender,
            contact_email=self.profile.email,
            contact_phone=self.profile.phone,
            payment_gateway_url=payment_url,
        )

    def prepare_hotel_handoff(
        self,
        hotel_name: str,
        city: str,
        nights: int,
        price_per_night: int,
    ) -> BookingSession:
        """Create a prepared hotel booking session landing on payment."""
        sess_id = f"BP-HTL-{uuid.uuid4().hex[:8].upper()}"
        base_amt = price_per_night * nights
        taxes = int(base_amt * 0.18)
        total = base_amt + taxes

        params = {
            "session": sess_id,
            "type": "hotel",
            "guest": self.profile.full_name,
            "hotel": hotel_name,
            "city": city,
            "amount": total,
        }
        payment_url = f"https://payment.makemytrip.com/hotels/checkout?{urllib.parse.urlencode(params)}"

        return BookingSession(
            session_id=sess_id,
            booking_type="Hotel",
            item_title=f"{hotel_name} ({city}) • {nights} Night(s)",
            amount_inr=base_amt,
            taxes_inr=taxes,
            convenience_fee_inr=0,
            total_payable_inr=total,
            passenger_name=self.profile.full_name,
            passenger_age=self.profile.age,
            passenger_gender=self.profile.gender,
            contact_email=self.profile.email,
            contact_phone=self.profile.phone,
            payment_gateway_url=payment_url,
        )
