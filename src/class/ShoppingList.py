"""
ShoppingList Class - INST326 Project 2
Part of DDM Grocery List System
"""

from typing import Dict, List, Optional
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
        format_shopping_list_display,
        # group_items_by_category
    )
except ImportError as e:
    print(f"Warning: Could not import necessary functions {e}")
    sys.exit(1)

# Import Ingredient class
from Ingredient import Ingredient


# ShoppingList Class
class ShoppingList:
    """
    Represents a compiled shopping list from multiple recipes.
    
    Aggregates ingredients from multiple recipes, handles quantity summation, unit conversion, & organization.

    Attributes:
        _items (dict): Aggregated ingredients with quatities & metadata
        _recipes (list): Names of recipes contributing to this shopping list
    
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
        """Initialize an empty shopping list"""
        self._items: Dict[str, Dict] = {}
        self._recipes: List[str] = []
    
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
        return f"ShoppingList(items={len(self._items)}, recipes={len(self._recipes)})"

    def add_ingredient(self, ingredient: Ingredient, recipe_name: str) -> None:
        """
        Add an ingredient to the shopping list
        
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

        # Validation
        if not isinstance(ingredient, Ingredient):
            raise TypeError("ingredient must be an Ingredient instance")
        if not recipe_name or not recipe_name.strip():
            raise ValueError("recipe_name cannot be empty")
        
        # Recipe's gotta be tracked
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
            # New item - add to list
            self._items[item_name] = {
                'quantity': ingredient._quantity,
                'unit': ingredient._unit,
                'recipes': [recipe_name],
                'preparation': ingredient._preparation
            }




   
if __name__ == "__main__":
    sl = ShoppingList()
    print(sl)  # Should print empty

    # adding some ingredients
    sl.add_ingredient(Ingredient("2 cups flour"), "Cookies")
    sl.add_ingredient(Ingredient("1 cup flour"), "Bread")
    sl.add_ingredient(Ingredient("3 eggs"), "Cookies")
    
    print(sl)
    print(repr(sl))
