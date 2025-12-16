"""
Test Suite for Composition Relationships
INST326 Project 3 - DDM Grocery List System

Tests that composition (has-a relationships) work correctly.
"""

import pytest
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.ShoppingList import ShoppingList
from src.models.Ingredient import Ingredient
from src.models.Store import AbstractStore, CSVStore
from src.recipe_parser import RecipeParser, TXTRecipeParser


class TestShoppingListComposition:
    """Test that ShoppingList demonstrates composition correctly."""
    
    def test_shopping_list_has_items(self):
        """ShoppingList HAS items (composition, not inheritance)."""
        sl = ShoppingList()
        
        # Shopping list should have _items attribute
        assert hasattr(sl, '_items')
        assert isinstance(sl._items, dict)
        
        # Add item
        sl.add_ingredient(Ingredient("2 cups flour"), "Cookies")
        
        # Shopping list now CONTAINS the item
        assert len(sl._items) > 0
        assert 'flour' in sl._items
    
    def test_shopping_list_has_recipes(self):
        """ShoppingList HAS recipes (composition, not inheritance)."""
        sl = ShoppingList()
        
        # Shopping list should have _recipes attribute
        assert hasattr(sl, '_recipes')
        assert isinstance(sl._recipes, list)
        
        # Add ingredients from recipes
        sl.add_ingredient(Ingredient("2 cups flour"), "Cookies")
        sl.add_ingredient(Ingredient("3 eggs"), "Cookies")
        sl.add_ingredient(Ingredient("1 cup sugar"), "Cake")
        
        # Shopping list now CONTAINS recipe names
        assert len(sl._recipes) > 0
        assert "Cookies" in sl._recipes
        assert "Cake" in sl._recipes
    
    def test_shopping_list_has_store_comparisons(self):
        """ShoppingList HAS store comparison data (composition)."""
        sl = ShoppingList()
        
        # Shopping list should have _store_comparisons attribute
        assert hasattr(sl, '_store_comparisons')
        assert isinstance(sl._store_comparisons, dict)
        
        # Add some items
        sl.add_ingredient(Ingredient("2 cups milk"), "Smoothie")
        
        # Create stores and compare
        stores = [CSVStore("safeway"), CSVStore("giant")]
        for store in stores:
            store.load_inventory()
        
        comparisons = sl.compare_stores(stores)
        
        # Shopping list now CONTAINS store comparison data
        assert len(sl._store_comparisons) > 0
    
    def test_shopping_list_is_not_ingredient(self):
        """ShoppingList does NOT inherit from Ingredient."""
        sl = ShoppingList()
        
        # ShoppingList should NOT be an instance of Ingredient
        assert not isinstance(sl, Ingredient)
        
        # It CONTAINS ingredients instead
        sl.add_ingredient(Ingredient("2 cups flour"), "Cookies")
        assert isinstance(list(sl._items.values())[0], dict)


class TestCompositionVsInheritance:
    """Test that composition is used where appropriate, not inheritance."""
    
    def test_shopping_list_uses_not_inherits_ingredient(self):
        """ShoppingList USES Ingredient objects (composition)."""
        sl = ShoppingList()
        ingredient = Ingredient("2 cups flour")
        
        # ShoppingList works WITH Ingredient
        sl.add_ingredient(ingredient, "Cookies")
        
        # But doesn't inherit from it
        assert not isinstance(sl, Ingredient)
        assert isinstance(ingredient, Ingredient)
    
    def test_shopping_list_uses_not_inherits_store(self):
        """ShoppingList USES Store objects (composition)."""
        sl = ShoppingList()
        sl.add_ingredient(Ingredient("2 cups milk"), "Smoothie")
        
        store = CSVStore("safeway")
        store.load_inventory()
        
        # ShoppingList works WITH Store
        comparisons = sl.compare_stores([store])
        
        # But doesn't inherit from it
        assert not isinstance(sl, AbstractStore)
        assert not isinstance(sl, CSVStore)
    
    def test_shopping_list_uses_not_inherits_recipe_parser(self):
        """ShoppingList USES RecipeParser objects (composition)."""
        sl = ShoppingList()
        
        # ShoppingList should work WITH RecipeParser
        # (This test depends on having a sample recipe file)
        # For now, just verify it doesn't inherit
        assert not isinstance(sl, RecipeParser)


class TestWorkingWithObjects:
    """Test how ShoppingList works WITH other objects."""
    
    def test_add_ingredient_works_with_ingredient_object(self):
        """add_ingredient() works WITH Ingredient object."""
        sl = ShoppingList()
        ingredient = Ingredient("2 cups flour")
        
        # Working WITH the ingredient object
        sl.add_ingredient(ingredient, "Cookies")
        
        # Ingredient data is now part of shopping list
        assert len(sl) == 1
        assert 'flour' in sl._items
    
    def test_compare_stores_works_with_store_objects(self):
        """compare_stores() works WITH Store objects."""
        sl = ShoppingList()
        sl.add_ingredient(Ingredient("2 cups milk"), "Smoothie")
        
        # Create store objects
        store1 = CSVStore("safeway")
        store2 = CSVStore("giant")
        
        store1.load_inventory()
        store2.load_inventory()
        
        # Working WITH store objects
        comparisons = sl.compare_stores([store1, store2])
        
        # Should have results for both stores
        assert len(comparisons) == 2
    
    def test_add_recipe_works_with_parser_object(self):
        """add_recipe() works WITH RecipeParser object."""
        sl = ShoppingList()
        
        # This test requires a sample recipe file
        # For now, test the method exists and accepts right types
        assert hasattr(sl, 'add_recipe')
        
        # Method signature should accept RecipeParser
        import inspect
        sig = inspect.signature(sl.add_recipe)
        params = list(sig.parameters.keys())
        assert 'recipe_parser' in params


class TestAggregationBehavior:
    """Test that ShoppingList properly aggregates contained objects."""
    
    def test_aggregates_same_ingredient_from_multiple_recipes(self):
        """Aggregates same ingredient from different recipes."""
        sl = ShoppingList()
        
        # Add flour from two different recipes
        sl.add_ingredient(Ingredient("2 cups flour"), "Cookies")
        sl.add_ingredient(Ingredient("1 cup flour"), "Bread")
        
        # Should have ONE flour entry with combined quantity
        assert len(sl) == 1
        assert 'flour' in sl._items
        assert sl._items['flour']['quantity'] == 3.0  # 2 + 1
    
    def test_tracks_which_recipes_use_ingredient(self):
        """Tracks which recipes contribute each ingredient."""
        sl = ShoppingList()
        
        # Add flour from two recipes
        sl.add_ingredient(Ingredient("2 cups flour"), "Cookies")
        sl.add_ingredient(Ingredient("1 cup flour"), "Bread")
        
        # Should track both recipes
        assert 'Cookies' in sl._items['flour']['recipes']
        assert 'Bread' in sl._items['flour']['recipes']
    
    def test_handles_multiple_stores_in_comparison(self):
        """Handles multiple stores in comparison."""
        sl = ShoppingList()
        sl.add_ingredient(Ingredient("2 cups milk"), "Smoothie")
        
        # Compare multiple stores
        stores = [
            CSVStore("safeway"),
            CSVStore("giant"),
            CSVStore("trader_joes")
        ]
        
        for store in stores:
            store.load_inventory()
        
        comparisons = sl.compare_stores(stores)
        
        # Should have comparison data for all stores
        assert len(comparisons) == 3


class TestCompositionBenefits:
    """Test benefits of using composition over inheritance."""
    
    def test_can_change_contained_objects_dynamically(self):
        """Can add/remove contained objects dynamically."""
        sl = ShoppingList()
        
        # Add ingredients
        sl.add_ingredient(Ingredient("2 cups flour"), "Cookies")
        assert len(sl) == 1
        
        # Remove ingredient
        sl.remove_item("flour")
        assert len(sl) == 0
        
        # Add different ingredient
        sl.add_ingredient(Ingredient("3 eggs"), "Cookies")
        assert len(sl) == 1
    
    def test_can_work_with_different_store_types(self):
        """Can work with any AbstractStore subclass."""
        sl = ShoppingList()
        sl.add_ingredient(Ingredient("2 cups milk"), "Smoothie")
        
        # Works with CSVStore
        csv_stores = [CSVStore("safeway")]
        for store in csv_stores:
            store.load_inventory()
        comparisons1 = sl.compare_stores(csv_stores)
        assert len(comparisons1) > 0
        
        # Could also work with other store types
        # (They're placeholders, so we just verify it doesn't crash)
        from models.Store import MockAPIStore
        api_stores = [MockAPIStore("whole_foods")]
        for store in api_stores:
            store.load_inventory()
        comparisons2 = sl.compare_stores(api_stores)
        assert len(comparisons2) > 0


# ======================================================================
#                    RUN TESTS
# ======================================================================

if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])