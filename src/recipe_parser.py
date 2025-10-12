#parse_txt_recipe — Medium
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
            cleaned = ln.strip().lstrip("-*• ").strip()
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
