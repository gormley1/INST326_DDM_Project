from __future__ import annotations

import sys
import os

from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple, Any, Union
from datetime import datetime
import math
import re

# Add parent directory to path so the program can import store_data
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import functions from our first project so we can reuse them (all helpers stores will use)
try:
    from store_data import (
        load_store_data,
        find_item_price,
        calculate_shopping_list_total
    )
except ImportError as e:
    raise ImportError(
        "Could not import functions from store_data.py. Make sure Store.py is in the same folder."
        ### Do we need to add a directory path to get out of class and go to src/store_data.py?
            # Resolved this with sys.path.insert line on line 24
    ) from e

# Type alias for location: can be a (lat, lon) tuple or a ZIP code
LocationType = Union[Tuple[float, float], str]

"""
Store Class Hierarchy - INST326 Project 3
Part of DDM Grocery List System

This class represents a grocery store.
It stores things like the name, rating, hours, and location.
It can also load inventory data, find item prices, and total up a shopping list.

Inheritance Hierarchy Design:
- AbstractStore (ABC) - Defines interface all stores must implement
- CSVStore - Loads inventory from CSV files (our current implementation)
- MockAPIStore - Placeholder for future API integration
- WebScraperStore - Placeholder for future web scraping

Inheritance Justification:
All stores need to: load inventory, find prices, calculate totals
But each does it differently: CSV reads files, API calls endpoints, scrapers parse HTML
This is a classic "is-a" relationship: CSVStore IS-A Store, APIStore IS-A Store
"""

# ======================================================================================================================
#                   ABSTRACT BASE CLASS
# ======================================================================================================================

class AbstractStore(ABC):
    """
    Abstract base class for all store types. Defines the interface that ALL stores must implement.
    Cannot be instantiated directly- must use a concrete subclass. 

    Demonstrates:
    1. Abstraction - Forces all stores to have certain methods
    2. Polymorphism - Each store type implements methods differently
    3. Inheritance - All stores inherit common functionality

    Attributes:
        _name (str): Store name (lowercase, normalized)
        _rating (float): Store rating 0-5
        _hours (dict): Operating hours by day of the week
        _location (LocationType): coordinates or ZIP code
        _inventory (dict): Loaded inventory data
    """

    def __init__(self,
                 name: str, rating: float = 0.0,
                 hours: Optional[Dict[str, Tuple[str, str]]] = None,
                 location: Optional[LocationType] = None):
        """Initialize store w/ basic attributes."""
        # Property setters for validation
        self.name = name
        self.rating = rating
        self.hours = hours if hours else {}
        self.location = location if location else (0.0, 0.0)
        self._inventory: Optional[Dict[str, Dict[str, Any]]] = None
    
    # ----------  ABSTRACT METHODS ----------
    # MUST be implemented by all subclasses

    @abstractmethod
    def load_inventory(self) -> None:
        """
        Load store inventory data.

        Abstract method - each store type loads differently:
        - CSVStore: reads CSV files (mock data, imported & reconfigured JSON, locally stored instances)
        - APIStore: calls API endpoints (Matt is going to develop this post-project as an extracurricular project)
        - WebScraperStore: scrapes websites (future development)

        Raises:
            NotImplementedError: If subclass doesn't implement 
        """
        pass

    @abstractmethod
    def price_for(self, item_name: str) -> Optional[Dict[str, Any]]:
        """
        Get price info for specific item.
        
        ABSTRACT METHOD - Each store type looks up differently:
        - CSVStore: searches loaded dictionary
        - APIStore: makes API call
        - WebScraperStore: scrapes product page
        
        Args:
            item_name (str): Item to look up
            
        Returns:
            dict: Price info or None if not found
            
        Raises:
            NotImplementedError: If subclass doesn't implement
        """
        pass

    # ---------- SHARED METHODS ----------
    # work the same or ALL store types (inherited)

    def checkout(self, shopping_list: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate total cost for shopping list.
        
        SHARED METHOD - Works same for all store types.
        Uses the abstract price_for() method polymorphically.
        
        Args:
            shopping_list (dict): Items with quantities
            
        Returns:
            dict: {'total': float, 'itemized': dict, 'not_found': list}
            
        Raises:
            RuntimeError: If inventory not loaded
        """
        if self._inventory is None:
            raise RuntimeError("Load inventory first before checkout")
        return calculate_shopping_list_total(shopping_list, self._inventory)
    
    def get_store_name(self) -> str:
        """Return store name. SHARED METHOD."""
        return self._name
    
    def get_rating(self) -> float:
        """Return store rating. SHARED METHOD."""
        return self._rating

    # ---------- Validation helper methods ----------

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
        # Handle AM/PM conversion
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
                raise ValueError("Each day should have a (start, end) time tuple")
            start, end = times
            start24 = AbstractStore._normalize_time_str(start)
            end24 = AbstractStore._normalize_time_str(end)
            result[day.lower()] = (start24, end24)
        return result

    # ---------- Properties ----------

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
        """Operating hours by day"""
        return self._hours

    @hours.setter
    def hours(self, value: Dict[str, Tuple[str, str]]) -> None:
        self._hours = self._normalize_hours_dict(value)

    @property
    def location(self) -> LocationType:
        """Store location (coords or zip)"""
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

    # --- Main store methods --- DOUBLE CHECK WHERE THESE BELONG

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

    # --- Extra utility helper methods ---

    def is_open(self, when: Optional[datetime] = None) -> bool:
        """Returns True if the store is open right now or at the given time."""
        when = when or datetime.now()
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
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

    def distance_km_to(self, other: "AbstractStore") -> Optional[float]:
        """Calculates distance between two stores if both have coordinates."""
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
        R = 6371.0 # earth radius in km
        return round(R * c, 3)

    def compare_total(self, other: "AbstractStore", shopping_list: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Compares the total cost of the same shopping list at two stores.
        
        Demonstrates Polymorphism:
        - Works with ANY store type: CSVStore, APIStore, etc.
        - Calls each store's checkout() which uses their specific price_for()
        """
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

    # ---------- String representations ----------

    def __repr__(self) -> str:
        count = len(self._inventory) if isinstance(self._inventory, dict) else 0
        return f"Store(name='{self._name}', rating={self._rating}, location={self._location}, items={count})"

    def __str__(self) -> str:
        loc = (f"lat={self._location[0]:.3f}, lon={self._location[1]:.3f}"
               if isinstance(self._location, tuple)
               else f"ZIP={self._location}")
        count = len(self._inventory) if isinstance(self._inventory, dict) else 0
        return f"{self._name.title()} (rating {self._rating:.1f}) — {loc} — {count} items loaded"
    
    __abstractmethods__ = frozenset({'load_inventory', 'price_for'})
### =======================================================================================================
###                 Concrete Store Implementations
### =======================================================================================================
class CSVStore(AbstractStore):
    """Represents a grocery store with details that loads inventory from CSV files.
    
    Polymorphism example:
    - Inherits from AbstractStore
    - Implements load_inventory() using CSV reading
    - Implements price_for() using dictionary lookup

    This is the original Store class, renamed and integrated into hierarchy.
    """
    def load_inventory(self, data_source: str = "csv") -> None:
        """Load inventory from CSV file. 

        Implements abstract method from AbstractStore (same method specifically applied to CSV behavior).

        Args: data_source (str): Must be 'csv' for this store type

        Raises:
            ValueError: If data_source isn't 'csv'
            FileNotFoundError: If CSV file not found
        """
        if data_source != "csv":
            raise ValueError(f"CSVStore only supports 'csv' data source, got: {data_source}")
        
        # use helper function from store_data.py
        self._inventory = load_store_data(self._name, data_source=data_source)

    def price_for(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Look up item price in loaded CSV data.
        
        Implements abstract method from AbstractStore (polymorphism behavior).

        Args- item_name(str): Item to look up

        Returns- dict: Price info or None if not found

        Raises - RuntimeError: If inventory not loaded yet
        """
        if self._inventory is None:
            raise RuntimeError("Load inventory first before checking prices")
        
        # use helper function from store_data.py
        return find_item_price(item_name, self._inventory)
    
class MockAPIStore(AbstractStore):
    """Placeholder for future API-based store.

    Polymorphism justification:
    - Inherits from AbstractStore
    - Implements load_inventory() with scraping placeholder
    - Implements price_for() with page scraping placeholder

    Currently, this just prints what it WOULD do in the future (so Matt can build it out w/ HTML, JS, Insomnia, Mockoon, etc.)
    Future implementation would make actual HTTP requests to store APIs.
    """

    def load_inventory(self, data_source: str = "api") -> None:
        """PLaceholder: Would scrape website for inventory.

        Implements abstract method from AbstractStore (polymorphism- web scraping)

        Args- data_source (str): Ignored for now        
        """
        print(f"[MockAPIStore] Would call API for {self._name} inventory")
        # Future: requests.get(f"https://{self._name}.com/api/inventory")
        self._inventory = {} # empty for now

    def price_for(self, item_name: str) -> Optional[Dict[str, Any]]:
        """
        Placeholder: Would query API for item price.
        
        Implements abstract method from AbstractStore.

        Args- item_name (str): Item to look up
            
        Returns - dict: Empty dict (placeholder)
        """
        if self._inventory is None:
            raise RuntimeError("Load inventory first before checking prices")
        
        print(f"[MockAPIStore] Would query API for '{item_name}' at {self._name}")
        # Future: requests.get(f"https://{self._name}.com/api/price/{item_name}")
        return None

class WebScraperStore(AbstractStore):
    """
    Placeholder for future web scraping store.
    
    Polymorphism Justification:
    - Inherits from AbstractStore
    - Implements load_inventory() with scraping placeholder
    - Implements price_for() with page scraping placeholder
    
    Currently just prints what it WOULD do. Future implementation
    would use BeautifulSoup/Selenium to scrape store websites.
    """
    
    def load_inventory(self, data_source: str = "web") -> None:
        """
        Placeholder: Would scrape website for inventory.
        
        Implements abstract method from AbstractStore (polymorphism).

        Args:
            data_source (str): Ignored for now
        """
        print(f"[WebScraperStore] Would scrape {self._name} website for inventory")
        # Future: BeautifulSoup(requests.get(f"https://{self._name}.com/products"))
        self._inventory = {}  # Empty for now
    
    def price_for(self, item_name: str) -> Optional[Dict[str, Any]]:
        """
        Placeholder: Would scrape product page for price.
        
        Implements abstract method from AbstractStore.

        Args - item_name (str): Item to look up
            
        Returns - dict: Empty dict (placeholder)
        """
        if self._inventory is None:
            raise RuntimeError("Load inventory first before checking prices")
        
        print(f"[WebScraperStore] Would scrape {self._name} page for '{item_name}'")
        # Future: BeautifulSoup(requests.get(f"https://{self._name}.com/product/{item_name}"))
        return None






# ======================================================================
#                    DEMONSTRATION CODE
# ======================================================================

def demo_polymorphism():
    """
    Demonstrate polymorphism with store hierarchy.
    
    Shows how the SAME code works with DIFFERENT store types.
    This is the power of polymorphism!
    """
    print("=== POLYMORPHISM DEMONSTRATION ===\n")
    
    # Create different types of stores
    stores = [
        CSVStore("safeway", rating=4.2),
        MockAPIStore("whole_foods", rating=4.5),
        WebScraperStore("trader_joes", rating=4.7)
    ]
    
    # Same method call, different behavior for each type!
    print("Loading inventory for all stores...")
    for store in stores:
        print(f"\n{store.get_store_name().title()}:")
        store.load_inventory()  # POLYMORPHIC CALL
        # CSVStore reads CSV, MockAPIStore would call API, WebScraperStore would scrape
    
    print("\n" + "="*50 + "\n")
    
    # Try looking up prices (only CSVStore will work with real data)
    print("Looking up 'milk' price at each store...")
    for store in stores:
        print(f"\n{store.get_store_name().title()}:")
        price_info = store.price_for("milk")  # POLYMORPHIC CALL
        if price_info:
            print(f"  Found: ${price_info.get('price', 0):.2f}")
        else:
            print(f"  Not found (placeholder store)")


def demo_inheritance():
    """
    Demonstrate inheritance relationships.
    
    Shows how all stores inherit common functionality.
    """
    print("\n=== INHERITANCE DEMONSTRATION ===\n")
    
    # All stores inherit from AbstractStore
    csv_store = CSVStore("safeway")
    api_store = MockAPIStore("whole_foods")
    
    print("Checking inheritance relationships:")
    print(f"CSVStore is instance of AbstractStore? {isinstance(csv_store, AbstractStore)}")
    print(f"MockAPIStore is instance of AbstractStore? {isinstance(api_store, AbstractStore)}")
    
    print("\nAll stores inherit common methods:")
    print(f"CSV store name: {csv_store.get_store_name()}")
    print(f"API store name: {api_store.get_store_name()}")
    
    print("\nAll stores inherit validation:")
    try:
        bad_store = CSVStore("")  # Should fail
    except ValueError as e:
        print(f"✓ Validation works: {e}")


if __name__ == "__main__":
    # Run demonstrations
    demo_inheritance()
    demo_polymorphism()
    
    print("\n" + "="*50)
    print("Store hierarchy successfully demonstrates:")
    print("  ✓ Inheritance (AbstractStore → concrete stores)")
    print("  ✓ Abstract Base Classes (ABC with @abstractmethod)")
    print("  ✓ Polymorphism (same interface, different implementations)")
    print("="*50)




