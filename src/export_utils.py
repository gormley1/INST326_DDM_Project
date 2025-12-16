# export_to_csv - (Matt)
def export_to_csv(shopping_list: dict, filename: str, include_prices: bool = True, categorize: bool = True) -> bool:
    """
    Export shopping list to CSV spreadsheet format.
    
    Args:
        shopping_list (dict): Shopping list from compile_shopping_list()
        filename (str): Output CSV file path
        include_prices (bool): Whether to include price column (default: True)
        categorize (bool): Organize by store category (default: True)
    
    Returns:
        bool: True if successful
    
    Raises:
        IOError: If unable to write file
    
    Example:
        >>> lst = {'tomato': {'quantity': 6, 'unit': 'count', 'recipes': ['Pasta']}}
        >>> export_to_csv(lst, 'shopping_list.csv')
        True
    """
    import csv
    from pathlib import Path
    
    try:
        # Ensure parent directory exists
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Define headers
        if include_prices:
            fieldnames = ['Item', 'Quantity', 'Unit', 'Used In', 'Price', 'Notes']
        else:
            fieldnames = ['Item', 'Quantity', 'Unit', 'Used In', 'Notes']
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Organize by category if requested (default)
            if categorize:
                categorized = group_items_by_category(shopping_list)
                
                # Write items organized by category
                for category, items in categorized.items():
                    # Write category header row
                    writer.writerow({
                        'Item': f"=== {category.upper()} ===",
                        'Quantity': '',
                        'Unit': '',
                        'Used In': '',
                        'Notes': ''
                    })
                    
                    # Write items in this category
                    for item_name, item_data in sorted(items.items()):
                        row = {
                            'Item': item_name.title(),
                            'Quantity': item_data.get('quantity', 0),
                            'Unit': item_data.get('unit', ''),
                            'Used In': ', '.join(item_data.get('recipes', [])),
                            'Notes': item_data.get('notes', '')
                        }
                        
                        if include_prices:
                            row['Price'] = f"${item_data.get('price', 0.0):.2f}"
                        
                        writer.writerow(row)
            else:
                # Simple alphabetical list
                for item_name, item_data in sorted(shopping_list.items()):
                    row = {
                        'Item': item_name.title(),
                        'Quantity': item_data.get('quantity', 0),
                        'Unit': item_data.get('unit', ''),
                        'Used In': ', '.join(item_data.get('recipes', [])),
                        'Notes': item_data.get('notes', '')
                    }
                    
                    if include_prices:
                        row['Price'] = f"${item_data.get('price', 0.0):.2f}"
                    
                    writer.writerow(row)
        
        print(f"✓ Shopping list exported to {filename}")
        return True
    
    except Exception as e:
        raise IOError(f"Error exporting to CSV: {e}")



# export_to_pdf - (Matt)
def export_to_pdf(shopping_list: dict, filename: str, title: str = "Shopping List", categorize: bool = True) -> bool:
    """
    Generate PDF shopping list organized by category.
    
    Args:
        shopping_list (dict): Shopping list from compile_shopping_list()
        filename (str): Output PDF file path
        title (str): Document title (default: "Shopping List")
        categorize (bool): Organize by category (default: True)
    
    Returns:
        bool: True if successful
    
    Raises:
        IOError: If unable to create PDF
        ImportError: If fpdf2 not installed
    
    Example:
        >>> lst = {'tomato': {'quantity': 6, 'unit': 'count'}}
        >>> export_to_pdf(lst, 'shopping_list.pdf')
        True
    """
    try:
        from fpdf import FPDF
    except ImportError:
        raise ImportError("fpdf2 library required. Install with: pip install fpdf2")
    
    from pathlib import Path
    from datetime import datetime
    
    try:
        # Group by category (commented out during bug fixing)
        #categorized = group_items_by_category(shopping_list)
        
        # Ensure parent directory exists
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 15, title, ln=True, align='C')
        
        # Date
        pdf.set_font('Arial', '', 10)
        date_str = datetime.now().strftime('%B %d, %Y')
        pdf.cell(0, 8, f"Generated: {date_str}", ln=True, align='C')
        pdf.ln(5)
        
        # Track total
        total_price = 0.0

        # -------- categorization option handling added during bug fixes -------
        if categorize:
            items_to_display = group_items_by_category(shopping_list)
        else: #simple alphabetical list w/out categories
            items_to_display = {'Items': shopping_list}
        # ----------------------------------------------------------------------
        
        # Process each category
        for category, items in items_to_display.items():
            if not items:
                continue
            
            # Category header (only if categorized)
            if categorize:
                pdf.set_font('Arial', 'B', 14)
                pdf.set_fill_color(230, 230, 250)
                pdf.cell(0, 10, f"  {category}", ln=True, fill=True)
                pdf.ln(2)
            
            # Items in this category
            pdf.set_font('Arial', '', 10)
            
            for item_name, item_data in sorted(items.items()):
                qty = item_data.get('quantity', 0)
                unit = item_data.get('unit', '')
                
                # Checkbox and item
                pdf.cell(10, 8, '[ ]', border=0)
                pdf.cell(100, 8, f"{item_name.title()}", border=0)
                pdf.cell(40, 8, f"{qty:.1f} {unit}", border=0, align='R')
                
                # Price if available
                price = item_data.get('price', 0.0)
                if price > 0:
                    pdf.cell(40, 8, f"${price:.2f}", border=0, align='R')
                    total_price += price
                
                pdf.ln()
            
            pdf.ln(3)
        
        # Total
        if total_price > 0:
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(150, 10, 'Estimated Total:', align='R')
            pdf.cell(40, 10, f"${total_price:.2f}", align='L')
        
        # Footer
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 5, 'Generated by Cornucopia Grocery Assistant', align='C')
        
        # Save
        pdf.output(filename)
        print(f"✓ PDF exported to {filename}")
        return True
    
    except Exception as e:
        raise IOError(f"Error creating PDF: {e}")



# export_to_txt - (Matt)
def export_to_txt(shopping_list: dict, filename: str, title: str = "Shopping List", categorize: bool = True) -> bool:
    """
    Export shopping list to plain text file.
    
    Uses the format_shopping_list_display() function for consistent formatting.
    
    Args:
        shopping_list (dict): Shopping list from compile_shopping_list()
        filename (str): Output text file path
        title (str): Optional custom title (default: "Shopping List")
        categorize (bool): Organize by store category (default: True)
    
    Returns:
        bool: True if successful
    
    Raises:
        IOError: If unable to write file
    
    Example:
        >>> lst = {'tomato': {'quantity': 6, 'unit': 'count', 'recipes': ['Pasta']}}
        >>> export_to_txt(lst, 'shopping_list.txt')
        True
    """
    from pathlib import Path
    from datetime import datetime
    
    try:
        # Ensure parent directory exists
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Organize by category if requested (default)
        if categorize:
            categorized = group_items_by_category(shopping_list)
            formatted_list = ""
            
            for category, items in categorized.items():
                formatted_list += f"\n{'='*50}\n"
                formatted_list += f"  {category.upper()}\n"
                formatted_list += f"{'='*50}\n\n"
                
                # Format items in this category
                for item_name, item_data in sorted(items.items()):
                    qty = item_data.get('quantity', 0)
                    unit = item_data.get('unit', '')
                    recipes = item_data.get('recipes', [])
                    recipes_str = ', '.join(recipes)
                    formatted_list += f"[ ] {qty} {unit} {item_name.title()} --- used in {recipes_str}\n"
                    
                    notes = item_data.get('notes', None)
                    if notes:
                        formatted_list += f"     Notes: {notes}\n"
                    formatted_list += "\n"
        else:
            # Use existing non-categorized format
            formatted_list = format_shopping_list_display(shopping_list)
        
        # Add header with custom title and date
        header = f"{title}\n"
        header += f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n"
        header += "=" * 50 + "\n\n"
        
        full_content = header + formatted_list
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"✓ Text file exported to {filename}")
        return True
    
    except Exception as e:
        raise IOError(f"Error exporting to text file: {e}")



# other export formats???
#
#
#
#



# group_items_by_category - (Matt)
def group_items_by_category(shopping_list: dict) -> dict:
    """
    Organize shopping list items by grocery store category/section.
    
    Args:
        shopping_list (dict): Flat shopping list
    
    Returns:
        dict: Shopping list organized by category
            {
                'Produce': {'tomato': {...}, 'lettuce': {...}},
                'Dairy': {'milk': {...}, 'cheese': {...}},
                ...
            }
    
    Example:
        >>> lst = {
        ...     'tomato': {'quantity': 6, 'unit': 'count'},
        ...     'milk': {'quantity': 1, 'unit': 'gallon'}
        ... }
        >>> grouped = group_items_by_category(lst)
        >>> 'Produce' in grouped
        True
        >>> 'tomato' in grouped['Produce']
        True
    """
    # Category mapping
    CATEGORY_MAP = {
        'Produce': [
            'tomato', 'lettuce', 'onion', 'garlic', 'carrot', 'celery', 
            'pepper', 'cucumber', 'potato', 'broccoli', 'spinach', 
            'mushroom', 'zucchini', 'squash', 'cabbage', 'corn', 'peas'
        ],
        'Dairy': [
            'milk', 'cheese', 'butter', 'yogurt', 'cream', 'sour cream',
            'cottage cheese', 'cream cheese', 'parmesan', 'mozzarella',
            'cheddar', 'eggs'
        ],
        'Meat & Seafood': [
            'chicken', 'beef', 'pork', 'turkey', 'fish', 'salmon',
            'shrimp', 'tuna', 'bacon', 'sausage', 'ground beef',
            'chicken breast', 'steak'
        ],
        'Canned Goods': [
            'tomato paste', 'tomato sauce', 'beans', 'corn', 'soup',
            'broth', 'stock', 'tuna', 'olives', 'pickles'
        ],
        'Pasta & Grains': [
            'pasta', 'rice', 'flour', 'bread', 'tortilla', 'quinoa',
            'oats', 'cereal', 'noodles', 'spaghetti', 'macaroni'
        ],
        'Spices & Seasonings': [
            'salt', 'pepper', 'cumin', 'paprika', 'oregano', 'basil',
            'thyme', 'rosemary', 'garlic powder', 'onion powder',
            'cinnamon', 'vanilla', 'chili powder', 'cayenne'
        ],
        'Baking': [
            'sugar', 'baking soda', 'baking powder', 'vanilla extract',
            'yeast', 'chocolate chips', 'cocoa powder', 'brown sugar',
            'powdered sugar', 'honey', 'syrup'
        ],
        'Condiments & Sauces': [
            'ketchup', 'mustard', 'mayonnaise', 'hot sauce', 'soy sauce',
            'vinegar', 'oil', 'olive oil', 'vegetable oil', 'dressing',
            'salsa', 'bbq sauce'
        ],
        'Frozen': [
            'frozen vegetables', 'ice cream', 'frozen pizza', 'frozen fruit'
        ],
        'Beverages': [
            'water', 'juice', 'soda', 'coffee', 'tea', 'wine', 'beer'
        ]
    }
    
    # Initialize categories
    categorized = {
        'Produce': {},
        'Dairy': {},
        'Meat & Seafood': {},
        'Canned Goods': {},
        'Pasta & Grains': {},
        'Spices & Seasonings': {},
        'Baking': {},
        'Condiments & Sauces': {},
        'Frozen': {},
        'Beverages': {},
        'Other': {}
    }
    
    # Categorize each item
    for item_name, item_data in shopping_list.items():
        item_lower = item_name.lower()
        category_found = False
        
        # Check each category
        for category, keywords in CATEGORY_MAP.items():
            # Check if item matches any keyword
            if any(keyword in item_lower for keyword in keywords):
                categorized[category][item_name] = item_data
                category_found = True
                break
        
        # If no category found, put in 'Other'
        if not category_found:
            categorized['Other'][item_name] = item_data
    
    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}



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

