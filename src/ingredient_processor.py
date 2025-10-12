# parse_ingredient_line





# normalize_ingredient_name — Other (Medium): Denis
from typing import Dict

def normalize_ingredient_name(raw_ingredient: str) -> str:
    """Return a simplified, standardized ingredient name.

    Beginner approach:
      - lowercase
      - trim
      - remove common descriptors (e.g., 'fresh', 'organic')
      - basic synonym mapping (e.g., 'green onion' -> 'scallion')
      - naive plural handling: drop trailing 's' if present and long enough

    Args:
        raw_ingredient (str): Original ingredient text.

    Returns:
        str: Normalized ingredient name (may be empty if input invalid).

    Examples:
        >>> normalize_ingredient_name("Fresh Tomatoes")
        'tomato'
        >>> normalize_ingredient_name("Green onion")
        'scallion'
    """
    if not isinstance(raw_ingredient, str) or not raw_ingredient.strip():
        return ""

    name = raw_ingredient.strip().lower()

    remove_words = ["fresh", "organic", "ripe", "kosher", "sea", "extra", "virgin", "raw", "whole"]
    for w in remove_words:
        name = name.replace(w, "")
    name = " ".join(name.split())  # collapse spaces

    synonyms: Dict[str, str] = {
        "green onion": "scallion",
        "spring onion": "scallion",
        "cilantro": "coriander",
        "roma tomato": "tomato",
        "plum tomato": "tomato"
    }
    if name in synonyms:
        name = synonyms[name]

    # very naive plural fixer
    if len(name) > 3 and name.endswith("s"):
        name = name[:-1]

    return name.strip()





# clean_ingredient_text





# convert_units
