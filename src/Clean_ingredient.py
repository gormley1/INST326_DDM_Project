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