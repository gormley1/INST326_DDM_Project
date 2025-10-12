# parse_ingredient_line - Darrell
def parse_ingredient_line(ingredient_string):
    """Break down ingredient string into parts.
    
    Args:
        ingredient_string (str): Single ingredient (e.g., "2 cups flour").
    
    Returns:
        dict: {'quantity': float, 'unit': str, 'item': str, 'preparation': None}
    
    Examples:
        >>> parse_ingredient_line("2 cups flour")
        {'quantity': 2.0, 'unit': 'cups', 'item': 'flour', 'preparation': None}
    """
    if not ingredient_string:
        return {'quantity': 0.0, 'unit': 'each', 'item': '', 'preparation': None}
    
    parts = ingredient_string.strip().split()
    
    # Default values
    quantity = 1.0
    unit = 'each'
    item = ingredient_string
    preparation = None
    
    # Try to get quantity from first part
    if len(parts) > 0:
        try:
            quantity = float(parts[0])
            
            # If we have at least 3 parts: quantity unit item
            if len(parts) >= 3:
                unit = parts[1].lower()
                item = ' '.join(parts[2:])
            # If we have 2 parts: quantity item
            elif len(parts) == 2:
                item = parts[1]
        except ValueError:
            # First part is not a number, treat whole thing as item
            item = ingredient_string
    
    # Check for preparation words
    prep_words = ['diced', 'chopped', 'minced', 'sliced']
    for prep in prep_words:
        if prep in item.lower():
            preparation = prep
            item = item.lower().replace(prep, '').strip()
            break
    
    return {
        'quantity': quantity,
        'unit': unit,
        'item': item.lower().strip(),
        'preparation': preparation
    }





# normalize_ingredient_name — Other (Medium): Denis
from typing import Dict

def normalize_ingredient_name(raw_ingredient: str) -> str:
    """Return a simplified, standardized ingredient name.

    Beginner approach:
      - lowercase
      - trim
      - remove common descriptors (e.g., 'fresh', 'organic')
      - basic synonym mapping (e.g., 'green onion' -> 'scallion')
      - naive plural handling: drop trailing 's' if present and long enough

    Args:
        raw_ingredient (str): Original ingredient text.

    Returns:
        str: Normalized ingredient name (may be empty if input invalid).

    Examples:
        >>> normalize_ingredient_name("Fresh Tomatoes")
        'tomato'
        >>> normalize_ingredient_name("Green onion")
        'scallion'
    """
    if not isinstance(raw_ingredient, str) or not raw_ingredient.strip():
        return ""

    name = raw_ingredient.strip().lower()

    remove_words = ["fresh", "organic", "ripe", "kosher", "sea", "extra", "virgin", "raw", "whole"]
    for w in remove_words:
        name = name.replace(w, "")
    name = " ".join(name.split())  # collapse spaces

    synonyms: Dict[str, str] = {
        "green onion": "scallion",
        "spring onion": "scallion",
        "cilantro": "coriander",
        "roma tomato": "tomato",
        "plum tomato": "tomato"
    }
    if name in synonyms:
        name = synonyms[name]

    # very naive plural fixer
    if len(name) > 3 and name.endswith("s"):
        name = name[:-1]

    return name.strip()





# clean_ingredient_text - Darrell
def clean_ingredient_text(text):
    """Clean ingredient text by removing bullets and extra spaces.
    
    Args:
        text (str): Raw ingredient text.
    
    Returns:
        str: Cleaned text.
    
    Examples:
        >>> clean_ingredient_text("  * 2 cups flour  ")
        '2 cups flour'
    """
    if not text:
        return ""
    
    # Remove common bullets from start
    text = text.strip()
    if text.startswith(('-', '*', '•')):
        text = text[1:].strip()
    
    # Remove extra spaces
    while '  ' in text:
        text = text.replace('  ', ' ')
    
    return text.strip()




# convert_units - Darrell
def convert_units(quantity, from_unit, to_unit, ingredient_type=None):
    """Convert between measurement units.
    
    Args:
        quantity (float): Amount to convert.
        from_unit (str): Original unit.
        to_unit (str): Target unit.
        ingredient_type: Not used (for future expansion).
    
    Returns:
        float: Converted quantity.
    
    Examples:
        >>> convert_units(2, 'cups', 'tbsp')
        32.0
        >>> convert_units(16, 'oz', 'lb')
        1.0
    """
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    # If same unit, just return original
    if from_unit == to_unit:
        return quantity
    
    # Volume conversions (everything in tablespoons)
    volume_to_tbsp = {
        'cup': 16,
        'cups': 16,
        'tbsp': 1,
        'tablespoon': 1,
        'tsp': 1/3,
        'teaspoon': 1/3,
    }
    
    # Weight conversions (everything in ounces)
    weight_to_oz = {
        'lb': 16,
        'pound': 16,
        'oz': 1,
        'ounce': 1,
    }
    
    # Try volume conversion
    if from_unit in volume_to_tbsp and to_unit in volume_to_tbsp:
        # Convert to tablespoons first
        in_tbsp = quantity * volume_to_tbsp[from_unit]
        # Then convert to target unit
        result = in_tbsp / volume_to_tbsp[to_unit]
        return round(result, 2)
    
    # Try weight conversion
    if from_unit in weight_to_oz and to_unit in weight_to_oz:
        # Convert to ounces first
        in_oz = quantity * weight_to_oz[from_unit]
        # Then convert to target unit
        result = in_oz / weight_to_oz[to_unit]
        return round(result, 2)
    
    # If can't convert, just return original
    return quantity
