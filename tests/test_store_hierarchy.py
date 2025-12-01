"""
Test Suite for Store Inheritance Hierarchy
INST326 Project 3 - DDM Grocery List System

Tests inheritance, polymorphism, and abstract base class implementation.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.Store import AbstractStore, CSVStore, MockAPIStore, WebScraperStore


class TestAbstractBaseClass:
    """Test that AbstractStore properly enforces abstract methods."""
    
    def test_cannot_instantiate_abstract_store(self):
        """Abstract base class cannot be instantiated directly."""
        with pytest.raises(TypeError, match="abstract"):
            # This should fail because AbstractStore has abstract methods
            store = AbstractStore("test_store")
    
    def test_abstract_methods_must_be_implemented(self):
        """Subclasses must implement all abstract methods."""
        
        # Create incomplete subclass (missing abstract methods)
        class IncompleteStore(AbstractStore):
            def load_inventory(self):
                pass
            # Missing: price_for()
        
        # Should fail to instantiate
        with pytest.raises(TypeError):
            incomplete = IncompleteStore("incomplete")


class TestInheritance:
    """Test inheritance relationships work correctly."""
    
    def test_all_stores_inherit_from_abstract_store(self):
        """All concrete store types inherit from AbstractStore."""
        csv_store = CSVStore("safeway")
        api_store = MockAPIStore("whole_foods")
        scraper_store = WebScraperStore("trader_joes")
        
        # Check inheritance using isinstance
        assert isinstance(csv_store, AbstractStore)
        assert isinstance(api_store, AbstractStore)
        assert isinstance(scraper_store, AbstractStore)
    
    def test_stores_inherit_shared_methods(self):
        """All stores inherit common methods from base class."""
        stores = [
            CSVStore("safeway", rating=4.2),
            MockAPIStore("whole_foods", rating=4.5),
            WebScraperStore("trader_joes", rating=4.7)
        ]
        
        for store in stores:
            # These methods are inherited from AbstractStore
            assert hasattr(store, 'get_store_name')
            assert hasattr(store, 'get_rating')
            assert hasattr(store, 'is_open')
            assert hasattr(store, 'distance_km_to')
            
            # Test they work
            assert isinstance(store.get_store_name(), str)
            assert isinstance(store.get_rating(), float)
    
    def test_stores_inherit_validation(self):
        """All stores inherit property validation from base class."""
        # Bad rating should fail for any store type
        with pytest.raises(ValueError, match="Rating"):
            CSVStore("test", rating=10)  # Rating > 5
        
        with pytest.raises(ValueError, match="Rating"):
            MockAPIStore("test", rating=-1)  # Rating < 0
        
        # Bad name should fail for any store type
        with pytest.raises(ValueError, match="Name"):
            CSVStore("")  # Empty name
        
        with pytest.raises(ValueError, match="Name"):
            WebScraperStore("   ")  # Whitespace only


class TestPolymorphism:
    """Test polymorphic behavior - same interface, different implementations."""
    
    def test_load_inventory_polymorphism(self):
        """Same method name, different behavior per store type."""
        stores = [
            CSVStore("safeway"),
            MockAPIStore("whole_foods"),
            WebScraperStore("trader_joes")
        ]
        
        # Same method call works for all types
        for store in stores:
            # This should not raise an error
            store.load_inventory()
            # Each store loads differently:
            # - CSVStore reads CSV file
            # - MockAPIStore would call API (placeholder)
            # - WebScraperStore would scrape website (placeholder)
    
    def test_price_for_polymorphism(self):
        """Same method name, different lookup behavior per store type."""
        stores = [
            CSVStore("safeway"),
            MockAPIStore("whole_foods"),
            WebScraperStore("trader_joes")
        ]
        
        # Load inventories first
        for store in stores:
            store.load_inventory()
        
        # Same method call, different implementations
        for store in stores:
            # This should not raise an error
            result = store.price_for("milk")
            # Each store looks up differently:
            # - CSVStore searches dictionary
            # - MockAPIStore would query API (returns None for now)
            # - WebScraperStore would scrape page (returns None for now)
    
    def test_polymorphic_list_processing(self):
        """Process list of different store types uniformly."""
        stores = [
            CSVStore("safeway", rating=4.2),
            MockAPIStore("whole_foods", rating=4.5),
            WebScraperStore("trader_joes", rating=4.7)
        ]
        
        # Process all stores with same code
        names = []
        ratings = []
        
        for store in stores:
            names.append(store.get_store_name())
            ratings.append(store.get_rating())
        
        assert len(names) == 3
        assert len(ratings) == 3
        assert all(isinstance(r, float) for r in ratings)


class TestCSVStore:
    """Test CSV-specific functionality."""
    
    def test_csv_store_loads_inventory(self):
        """CSVStore successfully loads from CSV file."""
        store = CSVStore("safeway")
        store.load_inventory()
        
        # Should have loaded inventory
        assert store.inventory is not None
        assert isinstance(store.inventory, dict)
    
    def test_csv_store_finds_prices(self):
        """CSVStore can look up item prices from loaded data."""
        store = CSVStore("safeway")
        store.load_inventory()
        
        # Look up item (depends on your CSV data)
        # This test assumes your mock data has common items
        result = store.price_for("milk")
        # Should return dict or None
        assert result is None or isinstance(result, dict)
    
    def test_csv_store_calculates_checkout(self):
        """CSVStore can calculate shopping list total."""
        store = CSVStore("safeway")
        store.load_inventory()
        
        # Simple shopping list
        shopping_list = {
            'milk': {'quantity': 1, 'unit': 'gallon'},
            'eggs': {'quantity': 2, 'unit': 'dozen'}
        }
        
        result = store.checkout(shopping_list)
        
        # Should return dict with expected keys
        assert isinstance(result, dict)
        assert 'total' in result
        assert 'itemized' in result
        assert 'not_found' in result


class TestPlaceholderStores:
    """Test placeholder stores work as expected."""
    
    def test_mock_api_store_placeholder_behavior(self):
        """MockAPIStore prints placeholder messages."""
        store = MockAPIStore("whole_foods")
        
        # Should load without error (just prints message)
        store.load_inventory()
        assert store.inventory is not None
        
        # Price lookup should return None (placeholder)
        result = store.price_for("milk")
        assert result is None
    
    def test_web_scraper_store_placeholder_behavior(self):
        """WebScraperStore prints placeholder messages."""
        store = WebScraperStore("trader_joes")
        
        # Should load without error (just prints message)
        store.load_inventory()
        assert store.inventory is not None
        
        # Price lookup should return None (placeholder)
        result = store.price_for("milk")
        assert result is None


class TestStoreComparison:
    """Test comparing multiple stores."""
    
    def test_compare_total_method(self):
        """Can compare costs between two stores."""
        store_a = CSVStore("safeway")
        store_b = CSVStore("giant")
        
        store_a.load_inventory()
        store_b.load_inventory()
        
        shopping_list = {
            'milk': {'quantity': 1, 'unit': 'gallon'}
        }
        
        comparison = store_a.compare_total(store_b, shopping_list)
        
        assert isinstance(comparison, dict)
        assert 'this_total' in comparison
        assert 'other_total' in comparison
        assert 'winner' in comparison
        assert 'savings' in comparison


# ======================================================================
#                    RUN TESTS
# ======================================================================

if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])