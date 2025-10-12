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