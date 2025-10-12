def extract_ingredients_from_text(text_block):
    """Extract ingredient lines from recipe text.
    
    Args:
        text_block (str): Recipe text containing ingredients.
    
    Returns:
        list: List of ingredient strings.
    
    Examples:
        >>> text = "Ingredients:\\n- 2 cups flour\\n- 1 tsp salt"
        >>> extract_ingredients_from_text(text)
        ['2 cups flour', '1 tsp salt']
    """
    if not text_block:
        return []
    
    lines = text_block.split('\n')
    ingredients = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Skip header lines
        lower_line = line.lower()
        if 'ingredient' in lower_line or 'direction' in lower_line:
            continue
        
        # Remove bullets and dashes at the start
        if line.startswith(('-', '*', '•')):
            line = line[1:].strip()
        
        # If line starts with a number, it's probably an ingredient
        if line and (line[0].isdigit() or line.startswith(('-', '*', '•'))):
            ingredients.append(line)
    
    return ingredients