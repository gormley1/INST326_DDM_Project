"""
Store Class - INST326 Project 2
Part of DDM Grocery List System

This class represents a grocery store.
It stores things like the name, rating, hours, and location.
It can also load inventory data, find item prices, and total up a shopping list.
"""

from __future__ import annotations
from typing import Dict, Optional, Tuple, Any, Union
from datetime import datetime
import math
import re

# Import functions from our first project so we can reuse them
try:
    from store_data import (
        load_store_data,
        find_item_price,
        calculate_shopping_list_total
    )
except ImportError as e:
    raise ImportError(
        "Could not import functions from store_data.py. Make sure store.py is in the same folder."
    ) from e


# Location can be a (lat, lon) tuple or a ZIP code
LocationType = Union[Tuple[float, float], str]


class Store:
    """Represents a grocery store with details and inventory."""

    def __init__(
        self,
        name: str,
        rating: float = 0.0,
        hours: Optional[Dict[str, Tuple[str, str]]] = None,
        location: Optional[LocationType] = None
    ):
        # Use properties so that validation runs automatically
        self.name = name
        self.rating = rating
        self.hours = hours if hours else {}
        self.location = location if location else (0.0, 0.0)
        self._inventory: Optional[Dict[str, Dict[str, Any]]] = None  # Will hold store data once loaded

    # --- Helper methods ---

    @staticmethod
    def _normalize_time_str(t: str) -> str:
        """Converts times like '8am', '8:30 PM', or '20:15' into 'HH:MM'."""
        if not isinstance(t, str) or not t.strip():
            raise ValueError("Invalid time format")
        s = t.strip().lower().replace('.', '').replace(' ', '')
        am = s.endswith('am')
        pm = s.endswith('pm')
        if am or pm:
            s = s[:-2]
        if ':' in s:
            hh, mm = s.split(':', 1)
        else:
            hh, mm = s, '00'
        if not hh.isdigit() or not mm.isdigit():
            match = re.match(r'^(\d{1,2})(?::?(\d{1,2}))?$', s)
            if not match:
                raise ValueError(f"Could not read time: {t}")
            hh = match.group(1)
            mm = match.group(2) or '00'
        h = int(hh)
        m = int(mm)
        if am and h == 12:
            h = 0
        elif pm and h != 12:
            h += 12
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError(f"Invalid time: {h}:{m}")
        return f"{h:02d}:{m:02d}"

    @staticmethod
    def _normalize_hours_dict(value: Dict[str, Tuple[str, str]]) -> Dict[str, Tuple[str, str]]:
        """Goes through the hours dict and normalizes all times."""
        if not isinstance(value, dict):
            raise ValueError("Hours must be a dictionary like {'mon': ('8am','9pm')}")
        result = {}
        for day, times in value.items():
            if not isinstance(times, tuple) or len(times) != 2:
                raise ValueError("Each day should have a start and end time tuple")
            start, end = times
            start24 = Store._normalize_time_str(start)
            end24 = Store._normalize_time_str(end)
            result[day.lower()] = (start24, end24)
        return result

    # --- Properties ---

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name must be a non-empty string")
        self._name = value.strip().lower()

    @property
    def rating(self) -> float:
        return self._rating

    @rating.setter
    def rating(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError("Rating must be a number")
        if not (0 <= value <= 5):
            raise ValueError("Rating must be between 0 and 5")
        self._rating = float(value)

    @property
    def hours(self) -> Dict[str, Tuple[str, str]]:
        return self._hours

    @hours.setter
    def hours(self, value: Dict[str, Tuple[str, str]]) -> None:
        self._hours = self._normalize_hours_dict(value)

    @property
    def location(self) -> LocationType:
        return self._location

    @location.setter
    def location(self, value: LocationType) -> None:
        # Allow ZIP or coordinates
        if isinstance(value, str):
            if not re.fullmatch(r'\d{5}', value.strip()):
                raise ValueError("ZIP code should be a 5-digit string")
            self._location = value.strip()
            return
        if not isinstance(value, tuple) or len(value) != 2:
            raise ValueError("Location must be (latitude, longitude) or ZIP string")
        lat, lon = value
        if not (isinstance(lat, (int, float)) and isinstance(lon, (int, float))):
            raise ValueError("Latitude and longitude must be numbers")
        self._location = (float(lat), float(lon))

    @property
    def inventory(self) -> Optional[Dict[str, Dict[str, Any]]]:
        return self._inventory

    # --- Main store methods ---

    def load_inventory(self, data_source: str = "csv") -> None:
        """Loads the store inventory using the load_store_data() function."""
        self._inventory = load_store_data(self._name, data_source=data_source)

    def price_for(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Returns the price info for an item."""
        if self._inventory is None:
            raise RuntimeError("Load the inventory first before checking prices")
        return find_item_price(item_name, self._inventory)

    def checkout(self, shopping_list: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates a total for the given shopping list."""
        if self._inventory is None:
            raise RuntimeError("Load the inventory first before checkout")
        return calculate_shopping_list_total(shopping_list, self._inventory)

    # --- Extra helper methods ---

    def is_open(self, when: Optional[datetime] = None) -> bool:
        """Returns True if the store is open right now or at the given time."""
        when = when or datetime.now()
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        today = days[when.weekday()]
        hours = self._hours.get(today)
        if not hours:
            return False
        start, end = hours
        try:
            start_mins = int(start[:2]) * 60 + int(start[3:])
            end_mins = int(end[:2]) * 60 + int(end[3:])
            now_mins = when.hour * 60 + when.minute
            return start_mins <= now_mins <= end_mins
        except Exception:
            return False

    def distance_km_to(self, other: "Store") -> Optional[float]:
        """Finds distance between two stores if both have coordinates."""
        if not (isinstance(self._location, tuple) and isinstance(other.location, tuple)):
            return None  # skip if one store uses ZIP
        lat1, lon1 = self._location
        lat2, lon2 = other.location
        rlat1, rlon1 = math.radians(lat1), math.radians(lon1)
        rlat2, rlon2 = math.radians(lat2), math.radians(lon2)
        dlat = rlat2 - rlat1
        dlon = rlon2 - rlon1
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        R = 6371.0
        return round(R * c, 3)

    def compare_total(self, other: "Store", shopping_list: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Compares the total cost of the same shopping list at two stores."""
        if self._inventory is None or other.inventory is None:
            raise RuntimeError("Make sure both stores have loaded their inventories first")
        result_a = self.checkout(shopping_list)
        result_b = other.checkout(shopping_list)
        total_a, total_b = result_a['total'], result_b['total']
        if abs(total_a - total_b) < 0.01:
            winner, savings = "tie", 0.0
        elif total_a < total_b:
            winner, savings = "self", round(total_b - total_a, 2)
        else:
            winner, savings = "other", round(total_a - total_b, 2)
        return {"this_total": total_a, "other_total": total_b, "winner": winner, "savings": savings}

    # --- String representations ---

    def __repr__(self) -> str:
        count = len(self._inventory) if isinstance(self._inventory, dict) else 0
        return f"Store(name='{self._name}', rating={self._rating}, location={self._location}, items={count})"

    def __str__(self) -> str:
        loc = (f"lat={self._location[0]:.3f}, lon={self._location[1]:.3f}"
               if isinstance(self._location, tuple)
               else f"ZIP={self._location}")
        count = len(self._inventory) if isinstance(self._inventory, dict) else 0
        return f"{self._name.title()} (rating {self._rating:.1f}) — {loc} — {count} items loaded"