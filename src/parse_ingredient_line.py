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