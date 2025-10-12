# load_store_data - ? (Matt)


#find_item_price — Other (Simple→Medium) (Denis)

from typing import Optional

def find_item_price(item_name: str, store_inventory: Dict[str, Dict[str, object]]) -> Optional[Dict[str, object]]:
    """Return price info for an item from a store inventory dict.

    The inventory is expected to look like:
      {
        'tomato paste': {'brand': 'Generic', 'price': 0.89, 'size': '6', 'unit': 'oz', 'category': 'canned goods', 'date_checked': '2025-10-01'},
        ...
      }

    Matching rules (very basic):
      1) exact lowercase match
      2) try adding/removing a trailing 's' for plural/singular

    Args:
        item_name (str): Standardized item name.
        store_inventory (dict): Inventory data as described above.

    Returns:
        dict | None: Price info dict if found; None otherwise.

    Raises:
        TypeError: If inputs are wrong types.

    Examples:
        >>> inv = {'tomato paste': {'price': 0.89}}
        >>> find_item_price('tomato paste', inv)['price']
        0.89
    """
    if not isinstance(item_name, str):
        raise TypeError("item_name must be a string")
    if not isinstance(store_inventory, dict):
        raise TypeError("store_inventory must be a dict")

    key = item_name.strip().lower()
    if not key:
        return None

    if key in store_inventory:
        return store_inventory[key]

    # plural/singular toggles
    if key.endswith("s") and key[:-1] in store_inventory:
        return store_inventory[key[:-1]]
    if (key + "s") in store_inventory:
        return store_inventory[key + "s"]

    return None

# calculate_shopping_list_total - Medium (Matt)

# compare_store_totals