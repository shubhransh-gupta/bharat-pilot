"""
Intercity bus route exploration and Volvo/Electric sleeper comparison.
"""

from dataclasses import dataclass
from typing import List, Optional
import urllib.parse


@dataclass
class BusOption:
    operator: str
    bus_type: str  # e.g., 'Bharat Benz AC Sleeper (2+1)', 'Volvo Multi-Axle'
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration: str
    rating: float
    price_inr: int
    seats_left: int
    boarding_point: str
    dropping_point: str
    booking_url: str = ""


class BusRadar:
    """Intercity bus comparison engine."""

    ROUTES = {
        ("BLR", "HYD"): [
            ("Zingbus Electric", "Electric AC Sleeper (2+1)", "22:00", "06:30", "8h 30m", 4.7, 850, 14, "Madiwala", "Gachibowli"),
            ("IntrCity SmartBus", "Volvo Multi-Axle AC Sleeper", "21:30", "06:00", "8h 30m", 4.6, 950, 8, "Indiranagar", "Ameerpet"),
            ("KSRTC Airavat", "Club Class Volvo Multi-Axle", "22:30", "07:00", "8h 30m", 4.5, 1100, 22, "Majestic Kempegowda", "MGBS"),
        ],
        ("DEL", "JAI"): [
            ("Zingbus", "Bharat Benz AC Seater (2+2)", "06:00", "11:00", "5h 00m", 4.6, 450, 18, "Kashmere Gate ISBT", "Sindhi Camp"),
            ("RSRTC Volvo", "Volvo Multi-Axle", "07:30", "12:45", "5h 15m", 4.4, 650, 12, "Bikaner House", "Narayan Singh Circle"),
        ],
        ("BOM", "GOA"): [
            ("VRL Travels", "I-Shift Volvo AC Multi-Axle Sleeper", "19:00", "07:30", "12h 30m", 4.6, 1250, 6, "Borivali West", "Mapusa"),
            ("Paulo Travels", "Mercedes Benz AC Multi-Axle", "18:30", "07:00", "12h 30m", 4.3, 1150, 11, "Dadar TT Circle", "Panjim"),
        ]
    }

    def search_buses(self, origin: str, destination: str) -> List[BusOption]:
        """Search intercity buses between two major cities."""
        key = (origin.upper()[:3], destination.upper()[:3])
        entries = self.ROUTES.get(key, self.ROUTES[("BLR", "HYD")])

        res = []
        for op, btype, dep, arr, dur, rat, price, left, bp, dp in entries:
            query = urllib.parse.urlencode({
                "from": origin,
                "to": destination,
                "operator": op,
                "source": "niffler"
            })
            direct_checkout = f"https://www.makemytrip.com/bus-tickets/?{query}"
            res.append(
                BusOption(
                    operator=op,
                    bus_type=btype,
                    origin=origin.title(),
                    destination=destination.title(),
                    departure_time=dep,
                    arrival_time=arr,
                    duration=dur,
                    rating=rat,
                    price_inr=price,
                    seats_left=left,
                    boarding_point=bp,
                    dropping_point=dp,
                    booking_url=direct_checkout,
                )
            )
        return sorted(res, key=lambda b: b.price_inr)
