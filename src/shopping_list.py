# shopping_list.py

# This script is designed to house all the processing logic for generation of shopping lists within our program
# (and handle errors as necessary).





#compile_shopping_list — Complex (Denis)

from typing import Dict, List, Tuple

def compile_shopping_list(
    recipe_list: List[Dict[str, object]],
    num_servings_dict: Dict[str, float]
) -> Dict[str, Dict[str, object]]:
    """Aggregate ingredients from multiple recipes into one shopping list.

    This beginner version uses a very simple parser inside the function:
    - It tries to split each ingredient line into: quantity, unit, item.
    - If it cannot parse, it treats the whole line as the item with quantity=1, unit='each'.
    - When combining duplicates, if units match, quantities are added.
      If units differ, it keeps the first seen unit and records a 'notes' flag.

    Args:
        recipe_list (list[dict]): Each dict has keys: 'name' (str), 'ingredients' (list[str]).
        num_servings_dict (dict[str, float]): Map of recipe name -> servings multiplier (e.g., 2.0).

    Returns:
        dict: {
            item_name (str): {
                'quantity': float,
                'unit': str,
                'recipes': list[str],
                'notes': str (optional when mismatched units occur)
            }, ...
        }

    Raises:
        TypeError: If inputs are not the expected types.

    Examples:
        >>> recipes = [
        ...   {'name': 'Pasta', 'ingredients': ['2 cup tomato', '1 lb pasta']},
        ...   {'name': 'Salad', 'ingredients': ['4 each tomato', '1 head lettuce']}
        ... ]
        >>> servings = {'Pasta': 1, 'Salad': 1}
        >>> lst = compile_shopping_list(recipes, servings)
        >>> 'tomato' in lst
        True
    """
    if not isinstance(recipe_list, list):
        raise TypeError("recipe_list must be a list")
    if not isinstance(num_servings_dict, dict):
        raise TypeError("num_servings_dict must be a dict")

    def _simple_parse(line: str) -> Tuple[float, str, str]:
        """Very small helper function.
        Tries formats like:
          - '2 cup tomato'
          - '3 cans beans'
          - 'tomato' (fallback -> 1 each tomato)
        Returns: (quantity, unit, item)
        """
        if not line or not isinstance(line, str):
            return (1.0, "each", "unknown")

        parts = line.strip().split()
        # Try: quantity unit item...
        if len(parts) >= 3:
            # quantity might be int/float
            q_str, unit = parts[0], parts[1]
            try:
                qty = float(q_str)
                item = " ".join(parts[2:]).strip()
                return (qty, unit.lower(), item.lower())
            except ValueError:
                # Not a number at the start -> fallback
                pass

        # Try: quantity item (assume unit 'each')
        if len(parts) >= 2:
            try:
                qty2 = float(parts[0])
                item2 = " ".join(parts[1:]).strip().lower()
                return (qty2, "each", item2)
            except ValueError:
                pass

        # Otherwise: just an item string
        return (1.0, "each", " ".join(parts).lower())

    shopping: Dict[str, Dict[str, object]] = {}

    for recipe in recipe_list:
        name = str(recipe.get("name", "Unknown"))
        ingredients = recipe.get("ingredients", [])
        servings = float(num_servings_dict.get(name, 1.0))

        if not isinstance(ingredients, list):
            continue  # skip if malformed

        for raw in ingredients:
            qty, unit, item = _simple_parse(str(raw))

            # scale by servings
            scaled_qty = qty * servings

            if item in shopping:
                entry = shopping[item]
                if entry["unit"] == unit:
                    entry["quantity"] += scaled_qty
                else:
                    # keep first unit; just record a note so a human can fix later
                    entry["quantity"] += scaled_qty  # still sum so we don't lose count
                    prev = entry.get("notes", "")
                    entry["notes"] = (prev + " | unit mismatch kept as "
                                      f"'{entry['unit']}', saw '{unit}'").strip()
                if name not in entry["recipes"]:
                    entry["recipes"].append(name)
            else:
                shopping[item] = {
                    "quantity": scaled_qty,
                    "unit": unit,
                    "recipes": [name]
                }

    # Round tiny float noise for nicer display
    for v in shopping.values():
        try:
            v["quantity"] = round(float(v["quantity"]), 3)
        except Exception:
            pass

    return shopping





# calculate_total_quantity - Medium (Matt)
def calculate_total_quantity(ingredient_entries: list[Dict[str, object]]) -> Dict[str, object]:
    """Sums quantities for the same ingredient across multiple recipes. 
    
    Args:
        ingredient_entries (list): List of ingredient dicts with 'quantity' and 'unit'
        
    Returns:
        dict: {'quantity': float, 'unit': str}
        
    Example:
        >>> entries = [
        ...     {'quantity': 2, 'unit': 'cups'},
        ...     {'quantity': 1, 'unit': 'cups'}
        ... ]
        >>> result = calculate_total_quantity(entries)
        >>> result['quantity']
        3.0
    """
    if not ingredient_entries:
        return {'quantity': 0, 'unit': 'unknown'}
    
    # Uses first entry's unit as base
    base_unit = ingredient_entries[0].get('unit', 'unknown')
    total_quantity = 0.0
    
    for entry in ingredient_entries:
        qty = entry.get('quantity', 0)
        unit = entry.get('unit', base_unit)
        if unit == base_unit:
            total_quantity += qty
        else:
            # For now, just add them (we could call convert_units here once that's written)
            total_quantity += qty
    
    return {
        'quantity': round(total_quantity, 3),
        'unit': base_unit
    }

# group_items_by_category


# validate_serving_size