# recipe_parser.py

# This script is designed to house all logic required to turn imported files into objects usable by 
# other processing logic in the program (and handle errors up front as necessary).

import os
from typing import Dict, List
import pdfplumber



# validate_file_format- Simple (Denis)
def validate_file_format(filepath: str) -> bool:
    """Return True if the file path has a supported recipe extension.

    Supported extensions: .txt, .docx, .pdf

    Args:
        filepath (str): Full or relative path to a file.

    Returns:
        bool: True if supported; False otherwise.

    Raises:
        TypeError: If filepath is not a string.

    Example:
        >>> validate_file_format("recipe.txt")
        True
        >>> validate_file_format("image.jpg")
        False
    """
    if not isinstance(filepath, str):
        raise TypeError("filepath must be a string")

    supported: List[str] = [".txt", ".docx", ".pdf"]
    _, ext = os.path.splitext(filepath)
    return ext.lower() in supported





# parse_recipe_file - Medium (Matt)
def parse_recipe_file(filepath: str) -> Dict[str, object]:
    """Main entry point for imported files; auto-detects format and routes to corresponding function.
    
    Args:
        filepath (str): Path to a file (MUST be str).

    Returns:
        output of corresponding parse_?_recipe(filepath) function matching input file type.    
    
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If no content could be parsed, or unsupported file type.

    Example:
        >>> recipe = parse_recipe_file("test.txt")
        >>> 'name' in recipe and 'ingredients' in recipe
        True
    """
    validate_file_format(filepath)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Recipe file not found for path '{filepath}'.")
    file_type = os.path.splitext(filepath)[1].lower()
    if file_type == '.txt':
        return parse_txt_recipe(filepath)
    # CONDITIONAL FOR .DOCX PARSE: uncomment when function is completed
    #elif file_type == '.docx':
        #return parse_docx_recipe(filepath)
    elif file_type == '.pdf':
        return parse_pdf_recipe(filepath)
    else:
        raise ValueError(f"Unsupported file format: {file_type}")
    




# extract_ingredients_from_text - Medium (Darrell) 
    # Created as a helper to simplify the parse_x_recipe functions 
    # while also making debugging quicker & easier bc they all use the same logic for ingredient extraction.
def extract_ingredients_from_text(text_block) -> List[str]:
    """Extract ingredient lines from recipe text.
    
    Args:
        text_block (str): Recipe text containing ingredients.
    
    Returns:
        list: List of ingredient strings.
    
    Example:
        >>> text = "Ingredients:\\n- 2 cups flour\\n- 1 tsp salt"
        >>> ingredients = extract_ingredients_from_text(text)
        >>> print(ingredients)
        ['2 cups flour', '1 tsp salt']
    """
    if not text_block:
        return []
    
    lines = text_block.split('\n')
    ingredients = []
    in_ingredients_section = False
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Skip header lines, check for entering ingredients section
        lower_line = line.lower()
        if 'ingredient' in lower_line: # removed -> or 'direction' in lower_line:
            in_ingredients_section = True
            continue

        # Check for leaving ingredients section (ex. if blank)
        if 'direction' in lower_line or 'instruction' in lower_line:
            in_ingredients_section = False
            break
        
        # Line processing if we're in ingredients section
        if in_ingredients_section:
            # Remove bullets and dashes at the start
            clean_line = line
            for bullet in ['-', '*', '•', '◦', '▪']:
                if clean_line.startswith(bullet):
                    clean_line = clean_line[1:].strip()
                    break
        
        # If line starts with a number & has content, or is after 'ingredients', it's probably an ingredient
        if clean_line and (clean_line[0].isdigit() or in_ingredients_section):
            ingredients.append(line)
    
    return ingredients
    




#parse_txt_recipe — Medium (Denis)
from typing import Dict

def parse_txt_recipe(filepath: str) -> Dict[str, object]:
    """Extract a very simple recipe structure from a plain .txt file.

    Expected shape:
        - First non-empty line = recipe name
        - A section that includes 'ingredients' (case-insensitive)
        - A section that includes 'directions' or 'instructions'

    Args:
        filepath (str): Path to a .txt file.

    Returns:
        dict: {'name': str, 'ingredients': list[str], 'directions': str}

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If no content could be parsed.

    Examples:
        >>> data = parse_txt_recipe("pasta.txt")
        >>> isinstance(data["ingredients"], list)
        True
    """
    if not isinstance(filepath, str):
        raise TypeError("filepath must be a string")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Recipe file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError("Recipe file is empty")

    lines = [ln.strip() for ln in content.split("\n")]
    # Name: first non-empty line
    name = next((ln for ln in lines if ln), "Untitled Recipe")

    # Find section starts
    ingredients_start = -1
    directions_start = -1
    for i, ln in enumerate(lines):
        low = ln.lower()
        if "ingredient" in low and ingredients_start == -1:
            ingredients_start = i + 1
        if ("direction" in low or "instruction" in low) and directions_start == -1:
            directions_start = i + 1

    # Gather ingredients
    ingredients: list[str] = []
    if ingredients_start != -1:
        end = directions_start - 1 if directions_start != -1 else len(lines)
        for ln in lines[ingredients_start:end]:
            # remove bullets
            cleaned = ln.strip() # removed -> .lstrip("-*• ").strip()
            # Matt added:
            for bullet in ['-', '*', '•', '◦', '▪']:
                if cleaned.startswith(bullet):
                    cleaned = cleaned[1:].strip()
                    break

            if cleaned and "ingredient" not in cleaned.lower():
                ingredients.append(cleaned)

    # Gather directions
    directions = ""
    if directions_start != -1:
        directions = "\n".join(lines[directions_start:]).strip()

    return {
        "name": name,
        "ingredients": ingredients,
        "directions": directions
    }





# parse_pdf_recipe - Complex (Matt)
    # largely based off Denis' parse_txt_recipe() function
def parse_pdf_recipe(filepath: str) -> Dict[str, object]:
    """Extract a very simple recipe structure from a .pdf file.

    Expected shape:
        - First non-empty line = recipe name
        - A section that includes 'ingredients' (case-insensitive)
        - A section that includes 'directions' or 'instructions'

    Args:
        filepath (str): Path to a .pdf file.

    Returns:
        dict: {'name': str, 'ingredients': list[str], 'directions': str}

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If no content could be parsed.

    Examples:
        >>> data = parse_pdf_recipe("chicken.pdf")
        >>> isinstance(data["ingredients"], list)
        True
    """
    if not isinstance(filepath, str):
        raise TypeError("filepath must be a string")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Recipe file not found: {filepath}")

    try:
        with pdfplumber.open(filepath) as pdf:
            full_text = '\n'.join([page.extract_text() or '' for page in pdf.pages])
    except Exception as e:
        raise ValueError(f"Could not read PDF file: {e}")

    if not full_text.strip():
        raise ValueError("Recipe file is empty or content is unreadable")

    lines = [ln.strip() for ln in full_text.split("\n")]
    # Name: first non-empty line
    name = next((ln for ln in lines if ln), "Untitled Recipe")

    # Find section starts
    ingredients_start = -1
    directions_start = -1
    for i, ln in enumerate(lines):
        low = ln.lower()
        if "ingredient" in low and ingredients_start == -1:
            ingredients_start = i + 1
        if ("direction" in low or "instruction" in low) and directions_start == -1:
            directions_start = i + 1

    # Gather ingredients
    ingredients: list[str] = []
    if ingredients_start != -1:
        end = directions_start - 1 if directions_start != -1 else len(lines)
        for ln in lines[ingredients_start:end]:
            # remove bullets
            cleaned = ln.strip() # removed -> .lstrip("-*• ").strip()
            # added:
            for bullet in ['-', '*', '•', '◦', '▪']:
                if cleaned.startswith(bullet):
                    cleaned = cleaned[1:].strip()
                    break

            if cleaned and "ingredient" not in cleaned.lower():
                ingredients.append(cleaned)

    # Gather directions
    directions = ""
    if directions_start != -1:
        directions = "\n".join(lines[directions_start:]).strip()

    return {
        "name": name,
        "ingredients": ingredients,
        "directions": directions
    }





# parse_docx_recipe NOT CLAIMED OR COMPLETED YET





# as we expand towards supporting other file types beyond .pdf, .docx, .txt, etc 
# (I was thinking .md, complete file support for everything exportable from Apple Notes + Files + other "competitor" apps 
# in the same space as us like ReciMe), we can write those parse_x_recipe() functions below here.



# FUTURE DEV SPACE: WORK IN PROGRESS BELOW





