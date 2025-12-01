"""
Ingredient Class - INST326 Project 2
Part of DDM Grocery List System
"""

from typing import Optional
import sys
import os

# Add parent directory to import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import helper functions from Project 1
try:
    from ingredient_processor import (
        parse_ingredient_line,
        normalize_ingredient_name,
        convert_units
    )
except ImportError as e:
    print(f"Warning: Could not import ingredient_processor: {e}")
    print("Make sure ingredient_processor.py is in the parent directory or same directory.")
    sys.exit(1)


class Ingredient:
    """Represents a single ingredient with quantity, unit, and item details.
    
    This class encapsulates ingredient data and provides methods for
    parsing, normalization, and unit conversion.
    
    Attributes:
        _quantity (float): Amount of ingredient needed
        _unit (str): Measurement unit (cups, tbsp, oz, etc.)
        _item (str): Normalized ingredient name
        _preparation (Optional[str]): Preparation method (diced, chopped, etc.)
        _raw_text (str): Original ingredient string
    
    Examples:
        >>> ing = Ingredient("2 cups flour")
        >>> ing.quantity
        2.0
        >>> ing.unit
        'cups'
        >>> ing.item
        'flour'
        
        >>> ing2 = Ingredient("1 1/2 tsp vanilla extract")
        >>> ing2.quantity
        1.5
    """
    
    def __init__(self, ingredient_string: str):
        """Initialize ingredient by parsing string.
        
        Args:
            ingredient_string (str): The raw ingredient string to parse.
        """
        parsed = parse_ingredient_line(ingredient_string)
        self._quantity: float = parsed['quantity']
        self._unit: str = parsed['unit']
        self._item: str = normalize_ingredient_name(parsed['item'])
        self._preparation: Optional[str] = parsed['preparation']
        self._raw_text: str = ingredient_string

    # The Ingredient class represents a single recipe ingredient as a structured, manipulable object. 
    # It automatically parses ingredient strings like "2 cups flour" or "1 1/2 tsp vanilla" 
    # into organized data with built-in validation and utility methods.

# Ex : python# Create and access
# ing = Ingredient("2 cups flour")
# print(ing.quantity)  # 2.0
# print(ing.item)      # 'flour'

# Scale recipe
# doubled = ing.scale(2.0)
# print(doubled)  # "4.0 cups flour"

# Convert units
# water = Ingredient("2 cups water")