"""
ShoppingList Class - INST326 Project 3
Part of DDM Grocery List System

Composition Demonstration: This class demonstrates composition, not inheritance.

We chose composition for this context bc ShoppingList HAS ingredients, recipes, & store comparison data.
Given ShoppingList is NOT a TYPE of ingredient or recipe, composition is the right choice
"""

from typing import Dict, List, Optional, TYPE_CHECKING
import sys
import os

# Parent Directory added to import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import helper functions (Project 01)
try:
    from ingredient_processor import (
        convert_units,
        normalize_ingredient_name,
        # calculate_total_quantity -> will need it, haven't written this function yet (or I can't find it)
    )
    # THESE FUNCTIONS HAVEN'T BEEN WRITTEN YET if commented out
    from export_utils import (
        # export_to_csv,
        # export_to_pdf,
        # export_to_txt,
        format_shopping_list_display,
        # group_items_by_category
    )
except ImportError as e:
    print(f"Warning: Could not import necessary functions {e}")
    sys.exit(1)

# Import Ingredient class
from .Ingredient import Ingredient

# TYPE_CHECKING allows type hints without circular imports
if TYPE_CHECKING:
    from Store import AbstractStore
    from recipe_parser import RecipeParser

# ShoppingList Class
class ShoppingList:
    """
    Represents a compiled shopping list from multiple recipes.
    
    Aggregates ingredients from multiple recipes, handles quantity summation, unit conversion, & organization.

    Demonstrates composition:
    - Has ingredients (self._items) 
    - Has recipes (self._recipes)  
    - Has store comparisons (self._store_comparisons) 
    - Works w/ Store objects 
    - Works w/ RecipeParser objects 

    NOT inheritance bc ShoppingList is not a type of ingredient, recipe, or store, but rather contains these objects.

    Attributes:
        _items (dict): Aggregated ingredients with quatities & metadata
        _recipes (list): Names of recipes contributing to this shopping list
        _store_comparisons (dict): Store pricing comparisons
    
    Examples:
        >>> shopping_list = ShoppingList()
        >>> shopping_list.add_ingredient(Ingredient("2 cups flour"), "Chocolate Chip Cookies")
        >>> shopping_list.add_ingredient(Ingredient("1 cup flour"), "Banana Bread")
        >>> len(shopping_list)
        1
        >>> print(shopping_list)
        3 cups flour
    """

    def __init__(self):
        """Initialize an empty shopping list

        Composition in action: creating empty containers that will hold other objects
        """
        self._items: Dict[str, Dict] = {} # ShoppingList HAS items
        self._recipes: List[str] = [] # ShoppingList HAS recipes
        self._store_comparisons: Dict[str, Dict] = {} # ShoppingList HAS store comparison data
    
    def __len__(self) -> int:
        """Return number of unique items in shopping list"""
        return len(self._items)
    
    def __str__(self) -> str:
        """Return human-readable shopping list"""
        if not self._items:
            return "Shopping List is EMPTY!!"
        
        output = f"Shopping List ({len(self._items)} items)\n"
        output += "-" * 40 + "\n"
        for item_name, item_data in self._items.items():
            output += f"- {item_data['quantity']:.2f} {item_data['unit']} {item_name}\n"
        return output
    
    def __repr__(self) -> str:
        """Return technical representation."""
        return (f"ShoppingList(items={len(self._items)}, recipes={len(self._recipes)}, stores_compared={len(self._store_comparisons)})")

# ---------- Ingredient Management ----------

    def add_ingredient(self, ingredient: Ingredient, recipe_name: str) -> None:
        """
        Add an ingredient to the shopping list

        Composition example: we're using an ingredient object (working with it), not inheriting from Ingredient (it becomes part of the program items collection)
        
        If the ingredient already exists, quantitites are summed.
        Unit conversion is applied if necessary.

        Args:
            ingredient (Ingredient): The ingredient to add
            recipe_name (str): Name of the recipe the ingredient comes from
        
        Raises:
            TypeError: if ingredient is not an Ingredient instance
            ValueError: if recipe_name is empty

        Examples:
            >>> sl = ShoppingList()
            >>> sl.add_ingredient(Ingredient("2 cups flour"), "Chocolate Chip Cookies)
            >>> len(sl)
            1
        """
        # In future, maybe recipe_name should come from Store (could be better with brand names/ store-specific ingredients)
        # Belay that order above don't know what I was thinking; recipe_name would have to come from user's recipe book (future class to complete) 

        # Validation
        if not isinstance(ingredient, Ingredient):
            raise TypeError("ingredient must be an Ingredient instance")
        if not recipe_name or not recipe_name.strip():
            raise ValueError("recipe_name cannot be empty")
        
        # Recipe's gotta be tracked (Composition: adding it to our recipes list)
        if recipe_name not in self._recipes:
            self._recipes.append(recipe_name)

        item_name = ingredient._item # should already be normalized via Ingredient.__init__

        # if item already exists, add quantities
        if item_name in self._items:
            existing = self._items[item_name]
        
            # check if the units match
            if existing['unit'] == ingredient._unit:
                # Same unit - just add
                existing['quantity'] += ingredient._quantity
            else:
                # Different units - try to convert
                try:
                    converted_qty = convert_units(
                        ingredient._quantity, 
                        ingredient._unit, 
                        existing['unit']
                    )
                    existing['quantity'] += converted_qty
                except Exception as e:
                    # If conversion fails, keep in original unit (or handle it differently)
                    print(f"Warning: Could not convert {ingredient._unit} to {existing['unit']}: {e}")
                    # for now, I'm just adding it as-is with original units
                    existing['quantity'] += ingredient._quantity
        
            # Track which recipes use this ingredient
            if recipe_name not in existing['recipes']:
                existing['recipes'].append(recipe_name)
        else:
            # New item - add to collection (composition)
            self._items[item_name] = {
                'quantity': ingredient._quantity,
                'unit': ingredient._unit,
                'recipes': [recipe_name],
                'preparation': ingredient._preparation
            }

    def add_recipe(self, recipe_parser: 'RecipeParser', servings: int = 1) -> None:
        """
        Add all ingredients from a recipe to the shopping list.
        
        Composition Justification:
        We're USING a RecipeParser object (working WITH it),
        not inheriting from RecipeParser, demonstrating the "has-a" relationship.
        
        Args:
            recipe_parser (RecipeParser): Parser containing recipe data
            servings (int): Number of servings to scale recipe
        
        Raises:
            ValueError: If servings is not positive
            
        Examples:
            >>> from recipe_parser import TXTRecipeParser
            >>> parser = TXTRecipeParser("pasta.txt")
            >>> parser.parse()
            >>> sl = ShoppingList()
            >>> sl.add_recipe(parser, servings=4)
        """
        if servings < 1:
            raise ValueError("Servings must be at least 1")
        
        # Get recipe data from parser (COMPOSITION: using another object)
        recipe_name = recipe_parser.get_recipe_name()
        ingredients = recipe_parser.get_ingredients()
        
        # Add each ingredient with scaling
        for ingredient_str in ingredients:
            # Parse ingredient string into Ingredient object
            ingredient = Ingredient(ingredient_str)
            
            # Scale quantity by servings
            ingredient._quantity *= servings
            
            # Add to list (reusing our add_ingredient method)
            self.add_ingredient(ingredient, recipe_name)
    
    def remove_item(self, item_name: str) -> bool:
        """
        Remove an item from the shopping list.
        
        Args:
            item_name (str): Name of item to remove
            
        Returns:
            bool: True if item was removed, False if not found
        """
        normalized_name = normalize_ingredient_name(item_name)
        if normalized_name in self._items:
            del self._items[normalized_name]
            return True
        return False
    
    def get_items(self) -> Dict[str, Dict]:
        """
        Get all items in shopping list.
        
        Returns:
            dict: Copy of items dictionary
        """
        return self._items.copy()
    
    def get_recipes(self) -> List[str]:
        """
        Get list of recipes contributing to this shopping list.
        
        COMPOSITION: Returning our contained recipe list.
        
        Returns:
            list: Copy of recipe names
        """
        return self._recipes.copy()     


    # ---------- STORE INTEGRATION ----------
    
    def compare_stores(self, stores: List['AbstractStore']) -> Dict[str, Dict]:
        """
        Compare shopping list cost across multiple stores.
        
        Composition Justification:
        We're using Store objects (working with them), not inheriting from Store.
        This demonstrates composition - ShoppingList HAS store comparisons.
        It isn't inheritance; we're not saying "ShoppingList IS-A Store", it works WITH stores
        
        Args:
            stores (list): List of AbstractStore objects to compare
            
        Returns:
            dict: Store comparisons sorted by total cost
            
        Raises:
            RuntimeError: If any store hasn't loaded inventory
            
        Examples:
            >>> from Store import CSVStore
            >>> sl = ShoppingList()
            >>> # ... add ingredients ...
            >>> stores = [CSVStore("safeway"), CSVStore("giant")]
            >>> for store in stores:
            ...     store.load_inventory()
            >>> comparisons = sl.compare_stores(stores)
        """
        self._store_comparisons = {}
        
        for store in stores:
            # Verify store has loaded inventory
            if store.inventory is None:
                raise RuntimeError(
                    f"Store '{store.get_store_name()}' must load inventory first"
                )
            
            # Calculate total at this store (COMPOSITION: using Store object)
            result = store.checkout(self._items)
            
            # Store comparison data (COMPOSITION: adding to our collection)
            self._store_comparisons[store.get_store_name()] = {
                'total': result['total'],
                'items_found': len(result['itemized']),
                'items_missing': len(result['not_found']),
                'itemized': result['itemized'],
                'not_found': result['not_found'],
                'store_object': store  # Keep reference to store (COMPOSITION)
            }
        
        # Sort by total cost (cheapest first)
        sorted_comparisons = dict(
            sorted(
                self._store_comparisons.items(),
                key=lambda x: x[1]['total']
            )
        )
        
        return sorted_comparisons
    
    def get_cheapest_store(self) -> Optional[str]:
        """
        Get name of cheapest store from comparisons.
        
        Returns - str: Store name, or None if no comparisons done
        """
        if not self._store_comparisons:
            return None
        
        cheapest = min(
            self._store_comparisons.items(),
            key=lambda x: x[1]['total']
        )
        return cheapest[0]
    
    def get_store_comparison(self, store_name: str) -> Optional[Dict]:
        """
        Get comparison data for specific store.
        
        Args - store_name (str): Store to look up
            
        Returns - dict: Comparison data or None if not found
        """
        return self._store_comparisons.get(store_name.lower())
    
    # ---------- DISPLAY & EXPORT ----------
    
    def format_for_display(self) -> str:
        """
        Format shopping list for console display.
        
        Returns:
            str: Formatted shopping list
        """
        return format_shopping_list_display(self._items)
    
    def get_summary(self) -> Dict:
        """
        Get summary statistics about shopping list.
        
        Returns:
            dict: Summary with item count, recipe count, etc.
        """
        return {
            'total_items': len(self._items),
            'total_recipes': len(self._recipes),
            'recipes': self._recipes.copy(),
            'stores_compared': len(self._store_comparisons),
            'cheapest_store': self.get_cheapest_store()
        }


# ----------------------------------------------------------------------
#                    DEMONSTRATION CODE
# ----------------------------------------------------------------------

def demo_composition():
    """
    Demonstrate composition relationships in ShoppingList.
    
    Supposed to show how ShoppingList CONTAINS other objects rather than
    inheriting from them.
    """
    print("=== COMPOSITION DEMONSTRATION ===\n")
    
    # Create shopping list (the container)
    shopping_list = ShoppingList()
    print(f"Created: {repr(shopping_list)}")
    
    # COMPOSITION: Adding ingredients (ShoppingList HAS ingredients)
    print("\n1. Adding ingredients (COMPOSITION):")
    shopping_list.add_ingredient(Ingredient("2 cups flour"), "Cookies")
    shopping_list.add_ingredient(Ingredient("1 cup flour"), "Bread")
    shopping_list.add_ingredient(Ingredient("3 eggs"), "Cookies")
    print(f"   Items: {len(shopping_list._items)}")
    print(f"   Recipes: {len(shopping_list._recipes)}")
    
    # COMPOSITION: ShoppingList contains multiple recipes
    print("\n2. Multiple recipes contribute (COMPOSITION):")
    for recipe in shopping_list.get_recipes():
        print(f"   - {recipe}")
    
    print("\n" + "="*50)
    print("ShoppingList demonstrates composition:")
    print("  ✓ HAS ingredients (not IS-A ingredient)")
    print("  ✓ HAS recipes (not IS-A recipe)")
    print("  ✓ HAS store data (not IS-A store)")
    print("  ✓ Works WITH other objects")
    print("="*50)























































   
if __name__ == "__main__":
    sl = ShoppingList()
    print(sl)  # Should print empty

    # adding some ingredients
    sl.add_ingredient(Ingredient("2 cups flour"), "Cookies")
    sl.add_ingredient(Ingredient("1 cup flour"), "Bread")
    sl.add_ingredient(Ingredient("3 eggs"), "Cookies")
    
    print(sl)
    print(repr(sl))
