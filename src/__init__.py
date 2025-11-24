
# src/__init__.py

"""
INST326_DDM_Project — Function library for grocery-list tool.
Package init file: exposes main parsing / processing modules at package level.
"""

# Package version
__version__ = "0.1.0"

# Import key modules so users have a simpler import path
from .recipe_parser import (
    validate_file_format,
    parse_recipe_file,
    parse_txt_recipe,
    parse_pdf_recipe,
    # assume you’ll have:
    parse_docx_recipe,
)
from .ingredient_processor import (
    convert_fraction,
    parse_ingredient_line,
    normalize_ingredient_name,
    clean_ingredient_text,
    convert_units,
)
from .shopping_list import (
    compile_shopping_list,
    calculate_total_quantity,
    group_items_by_category,
    format_shopping_list_display,
)
from .store_data import (
    load_store_data,
    find_item_price,
    calculate_shopping_list_total,
)
from .export_utils import (
    export_to_csv,
    export_to_pdf,
    # possibly more
)

# Define what is publicly available when someone does: from src import *
__all__ = [
    "validate_file_format",
    "parse_recipe_file",
    "parse_txt_recipe",
    "parse_pdf_recipe",
    "parse_docx_recipe",
    "convert_fraction",
    "parse_ingredient_line",
    "normalize_ingredient_name",
    "clean_ingredient_text",
    "convert_units",
    "compile_shopping_list",
    "calculate_total_quantity",
    "group_items_by_category",
    "format_shopping_list_display",
    "load_store_data",
    "find_item_price",
    "calculate_shopping_list_total",
    "export_to_csv",
    "export_to_pdf",
    "__version__",
]
"""
Package initialization for recipe parsing module.

This exposes the inheritance hierarchy:
- RecipeParser (abstract base class)
- TXTRecipeParser
- PDFRecipeParser
- DOCXRecipeParser

Importing example:
    from recipe_parser import TXTRecipeParser
"""

__all__ = [
    "RecipeParser",
    "TXTRecipeParser",
    "PDFRecipeParser",
    "DOCXRecipeParser",
]
