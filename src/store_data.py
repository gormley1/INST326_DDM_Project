# store_data.py

# This script is designed to handle all logic relating to data from different grocery stores (just mock data for now).
from typing import Dict






# load_store_data - Medium (Matt)
import csv
import os

def load_store_data(store_name: str, data_source: str = 'csv') -> Dict[str, Dict[str, object]]:
    """Load mock (for now) grocery store inventory and pricing data.
    
    Args:
        store_name (str): Store name (e.g., 'safeway', 'giant')
        data_source (str): Data format, default 'csv'
        
    Returns:
        dict: Store inventory with prices
        
    Raises:
        FileNotFoundError: If store data file not found
        
    Examples:
        >>> inventory = load_store_data('safeway')
        >>> isinstance(inventory, dict)
        True
    """
    if data_source != 'csv':
        raise ValueError(f"Only 'csv' data source supported, got: {data_source}")
    # we'll have to come back and change this above bit when/if we move beyond mock store data to user reciept input
    
    filepath = f'data/mock_stores/{store_name}_inventory.csv'
    # same thing as above, the filepath will get changed from 'mock_stores/...' to wherever user pricing input data gets stored
        # on a larger scale note, I'm thinking that kind of data should be stored locally... meaning users should have:
        # 1. "their purchases": a local database of their recorded purchases that they've logged
        # 2. "public purchases": maybe an imported or called database that gets continually updated (but the more local we can make it the better)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Store data not found: {filepath}")
    
    inventory = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                item_name = row['item_name'].lower().strip()
                inventory[item_name] = {
                    'brand': row.get('brand', ''),
                    'price': float(row.get('price', 0)),
                    'size': row.get('package_size', ''),
                    'unit': row.get('unit', ''),
                    'category': row.get('category', ''),
                    'date_checked': row.get('date_checked', '')
                }
    except Exception as e:
        print(f"Error loading store data: {e}")
        return {}
    
    return inventory





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
def calculate_shopping_list_total(
    shopping_list: Dict[str, Dict[str, object]], 
    store_inventory: Dict[str, Dict[str, object]]
) -> Dict[str, object]:
    """Calculate total cost for shopping list at specific store.
    
    Args:
        shopping_list (dict): From compile_shopping_list()
        store_inventory (dict): From load_store_data()
        
    Returns:
        dict: {
            'total': float,
            'itemized': dict,
            'not_found': list
        }
        
    Examples:
        >>> shopping = {'tomato': {'quantity': 2, 'unit': 'count'}}
        >>> inventory = {'tomato': {'price': 0.50}}
        >>> result = calculate_shopping_list_total(shopping, inventory)
        >>> result['total']
        1.0
    """
    total_cost = 0.0
    itemized = {}
    not_found = []
    
    for item_name, item_data in shopping_list.items():
        # Look up price in inventory
        if item_name in store_inventory:
            price_info = store_inventory[item_name]
            quantity = item_data.get('quantity', 0)
            unit_price = price_info.get('price', 0.0)
            item_total = quantity * unit_price
            
            itemized[item_name] = {
                'quantity': quantity,
                'unit': item_data.get('unit', ''),
                'unit_price': unit_price,
                'total': round(item_total, 2)
            }
            
            total_cost += item_total
        else:
            # Try with/without 's' for plural matching
            found = False
            # Try adding 's'
            if item_name + 's' in store_inventory:
                price_info = store_inventory[item_name + 's']
                found = True
            # Try removing 's'
            elif item_name.endswith('s') and item_name[:-1] in store_inventory:
                price_info = store_inventory[item_name[:-1]]
                found = True
            
            if found:
                quantity = item_data.get('quantity', 0)
                unit_price = price_info.get('price', 0.0)
                item_total = quantity * unit_price
                
                itemized[item_name] = {
                    'quantity': quantity,
                    'unit': item_data.get('unit', ''),
                    'unit_price': unit_price,
                    'total': round(item_total, 2)
                }
                total_cost += item_total
            else:
                not_found.append(item_name)
    
    return {
        'total': round(total_cost, 2),
        'itemized': itemized,
        'not_found': not_found
    }





# compare_store_totals
def compare_store_totals(shopping_list: Dict[str, Dict[str, object]], store_list: list) -> Dict[str, Dict]:
    """Compare total costs across multiple stores.
    
    Args:
        shopping_list (dict): Shopping list from compile_shopping_list()
        store_list (list): List of store names to compare (e.g., ['safeway', 'giant'])
        
    Returns:
        dict: Store comparison sorted by total cost (cheapest first)
            {
                'giant': {'total': 43.21, 'items_found': 28, 'items_missing': 2},
                'safeway': {'total': 47.32, 'items_found': 29, 'items_missing': 1},
                'trader_joes': {'total': 51.15, 'items_found': 27, 'items_missing': 3}
            }
    
    Examples:
        >>> shopping_list = {'milk': {'quantity': 1, 'unit': 'gallon'}}
        >>> comparison = compare_store_totals(shopping_list, ['safeway', 'giant', 'trader_joes'])
        >>> cheapest = list(comparison.keys())[0]
        >>> print(f"Best store: {cheapest}")
        Best store: giant
    """
    comparison = {}
    
    for store_name in store_list:
        try:
            # Load store inventory
            inventory = load_store_data(store_name)
            
            # Calculate total for this store
            result = calculate_shopping_list_total(shopping_list, inventory)
            
            comparison[store_name] = {
                'total': result['total'],
                'items_found': len(result['itemized']),
                'items_missing': len(result['not_found'])
            }
            
        except FileNotFoundError:
            print(f"⚠️  Warning: Could not load data for {store_name}")
            comparison[store_name] = {
                'total': float('inf'),  # Mark as unavailable
                'items_found': 0,
                'items_missing': len(shopping_list)
            }
            
        except Exception as e:
            print(f"⚠️  Warning: Error processing {store_name}: {e}")
            comparison[store_name] = {
                'total': float('inf'),
                'items_found': 0,
                'items_missing': len(shopping_list)
            }
    
    # Sort by total cost (cheapest first)
    sorted_comparison = dict(
        sorted(comparison.items(), key=lambda x: x[1]['total'])
    )
    
    return sorted_comparison