def group_items_by_category(shopping_list):
    """Organize shopping list items by grocery store category.
    
    Args:
        shopping_list (dict): Flat shopping list from compile_shopping_list().
    
    Returns:
        dict: Shopping list organized by category.
    
    Examples:
        >>> shopping = {'tomato': {'quantity': 6, 'unit': 'count'}}
        >>> grouped = group_items_by_category(shopping)
        >>> 'produce' in grouped
        True
    """
    # Category mapping - which items belong to which store section
    category_map = {
        'produce': ['tomato', 'lettuce', 'onion', 'garlic', 'carrot', 'celery', 
                    'pepper', 'cucumber', 'potato', 'broccoli', 'spinach', 'scallion'],
        'dairy': ['milk', 'cheese', 'butter', 'yogurt', 'cream', 'sour cream', 'egg'],
        'meat': ['chicken', 'beef', 'pork', 'turkey', 'fish', 'salmon', 'bacon'],
        'canned_goods': ['tomato paste', 'bean', 'corn', 'soup', 'broth', 'tuna'],
        'pasta_grains': ['pasta', 'rice', 'flour', 'bread', 'tortilla', 'noodle'],
        'spices': ['salt', 'pepper', 'cumin', 'paprika', 'oregano', 'basil', 'coriander'],
        'baking': ['sugar', 'baking soda', 'baking powder', 'vanilla', 'yeast'],
    }
    
    # Create empty categories
    categorized = {
        'produce': {},
        'dairy': {},
        'meat': {},
        'canned_goods': {},
        'pasta_grains': {},
        'spices': {},
        'baking': {},
        'other': {}
    }
    
    # Sort each item into a category
    for item_name, item_data in shopping_list.items():
        category_found = False
        
        # Check each category to see if item belongs there
        for category, items in category_map.items():
            if item_name.lower() in items:
                categorized[category][item_name] = item_data
                category_found = True
                break
        
        # If item doesn't match any category, put in 'other'
        if not category_found:
            categorized['other'][item_name] = item_data
    
    # Remove empty categories
    categorized = {k: v for k, v in categorized.items() if v}
    
    return categorized