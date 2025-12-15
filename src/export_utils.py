# def export_to_csv

# def export_to_pdf

# def export_to_txt

# other export formats???

# group_items_by_category



# format_shopping_list_display - (Matt)
def format_shopping_list_display(shopping: dict) -> str:
    """ Formats input shopping list as a readable string for console/text output.

    Args:
        shopping (dict): shopping list generated from compile_shopping_list()

    Returns:
        grocery_list (str): formatted multi-line str

    Example:
        >>> lst = {'tomato': {'quantity': 6, 'unit': 'count', 'recipes': ['Pasta']}}
        >>> output = format_shopping_list_display(lst)
        >>> '[ ] 6 count Tomato - for Pasta' in output
        True
    """
    if not shopping:
        return "Your grocery list is empty!"
    
    grocery_list = "Grocery List\n"
    grocery_list += "-" * 50 + "\n\n"

    # Intake shopping list dictionary, loop through items
    for item_name, item_data in sorted(shopping.items()):
        # extract data
        qty = item_data.get('quantity', 0)
        unit = item_data.get('unit', '')
        recipes = item_data.get('recipes', [])
        recipes_str = ', '.join(recipes)
        grocery_list += f"[ ] {qty} {unit} {item_name.title()} --- used in {recipes_str}\n"
        # once the pricing functionality is working, {total_cost}: will go in front of {qty}
        notes = item_data.get('notes', None)
        if notes:
            grocery_list += f"     Notes: {notes}\n"
        grocery_list += "\n"

    # Eventually want this to organize ingredients by store, then by category (produce, meat, frozen, etc.)
        # nonessential logic- this can be updated later

    # will need more advanced logic in the future to intake parameters for
    # which ingredients will be sourced from what store (write a helper function); 
    # final list would have hierarchy like: 
        # store -> category -> item
    
    # Calculate total price if prices are available
    total = sum(item.get('price', 0) for item in shopping.values())
    if total > 0:
        grocery_list += f"ESTIMATED TOTAL: ${total:.2f}\n"
        # this should include state sales tax eventually

    return grocery_list