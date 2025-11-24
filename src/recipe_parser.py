"""
Recipe Parser Inheritance Hierarchy
INST326 - Fall 2025
Team Member: Darrell Cox - Documentation Lead

Implements an inheritance hierarchy for parsing recipes from different file formats.
Supports .txt, .pdf, .docx formats with unified ingredient extraction and structure.
"""

import os
import re
from abc import ABC, abstractmethod
from typing import Dict, List
import PyPDF2  # Must be installed
# python-docx imported lazily inside DOCX parser


# ======================================================================
#                           BASE CLASS
# ======================================================================

class RecipeParser(ABC):
    """Abstract base class for all recipe parsers."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.recipe_data = {}

    @abstractmethod
    def parse(self) -> Dict:
        """Parse the file into structured recipe data."""
        pass

    @abstractmethod
    def validate_format(self) -> bool:
        """Check if the file exists and is the expected format."""
        pass

    # ---------- Shared Ingredient Parsing Utilities ----------

    def extract_ingredients_section(self, text: str) -> List[str]:
        """
        Extract ingredient lines located between 'Ingredients:' and 'Directions:'.
        """
        lines = text.split("\n")
        ingredients = []
        in_section = False

        for line in lines:
            clean = line.strip()

            if re.match(r"^ingredients?:?$", clean, re.IGNORECASE):
                in_section = True
                continue

            if re.match(r"^(directions?|instructions?|steps?):?$", clean, re.IGNORECASE):
                break

            if in_section and clean:
                clean = re.sub(r"^[\-•*]\s*", "", clean)
                ingredients.append(clean)

        return ingredients

    def clean_ingredient_text(self, text: str) -> str:
        """Remove bullet characters & trim whitespace."""
        text = re.sub(r"^[\-•*◦▪▫→]\s*", "", text)
        return " ".join(text.split()).strip()

    # ---------- Convenience Accessors ----------

    def get_recipe_name(self) -> str:
        return self.recipe_data.get("name", "Untitled Recipe")

    def get_ingredients(self) -> List[str]:
        return self.recipe_data.get("ingredients", [])


# ======================================================================
#                         TXT PARSER
# ======================================================================

class TXTRecipeParser(RecipeParser):

    def validate_format(self) -> bool:
        return self.filepath.endswith(".txt") and os.path.isfile(self.filepath)

    def parse(self) -> Dict:
        if not self.validate_format():
            raise ValueError(f"Invalid TXT file: {self.filepath}")

        with open(self.filepath, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        name = lines[0].strip() if lines else "Untitled Recipe"

        ingredients = [self.clean_ingredient_text(i)
                       for i in self.extract_ingredients_section(content)]

        # Directions extraction
        directions = []
        in_directions = False
        for line in lines:
            line_clean = line.strip()
            if re.match(r"^(directions?|instructions?|steps?):?$", line_clean, re.IGNORECASE):
                in_directions = True
                continue
            if in_directions and line_clean:
                directions.append(line_clean)

        self.recipe_data = {
            "name": name,
            "ingredients": ingredients,
            "directions": directions,
            "source_file": self.filepath,
            "format": "txt",
        }

        return self.recipe_data


# ======================================================================
#                         PDF PARSER
# ======================================================================

class PDFRecipeParser(RecipeParser):

    def validate_format(self) -> bool:
        if not self.filepath.endswith(".pdf") or not os.path.isfile(self.filepath):
            return False
        try:
            with open(self.filepath, "rb") as f:
                PyPDF2.PdfReader(f)
            return True
        except Exception:
            return False

    def parse(self) -> Dict:
        if not self.validate_format():
            raise ValueError(f"Invalid PDF file: {self.filepath}")

        full_text = ""

        with open(self.filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                txt = page.extract_text()
                if txt:
                    full_text += txt + "\n"

        lines = [l.strip() for l in full_text.split("\n") if l.strip()]
        name = lines[0] if lines else "Untitled Recipe"

        ingredients = [self.clean_ingredient_text(i)
                       for i in self.extract_ingredients_section(full_text)]

        # Directions
        directions = []
        in_directions = False
        for line in lines:
            if re.match(r"^(directions?|instructions?|steps?):?$", line, re.IGNORECASE):
                in_directions = True
                continue
            if in_directions:
                directions.append(line)

        self.recipe_data = {
            "name": name,
            "ingredients": ingredients,
            "directions": directions,
            "source_file": self.filepath,
            "format": "pdf",
        }

        return self.recipe_data


# ======================================================================
#                         DOCX PARSER
# ======================================================================

class DOCXRecipeParser(RecipeParser):

    def validate_format(self) -> bool:
        if not self.filepath.endswith(".docx") or not os.path.isfile(self.filepath):
            return False
        try:
            from docx import Document
            Document(self.filepath)
            return True
        except Exception:
            return False

    def parse(self) -> Dict:
        if not self.validate_format():
            raise ValueError(f"Invalid DOCX file: {self.filepath}")

        from docx import Document
        doc = Document(self.filepath)

        full_text = "\n".join([p.text for p in doc.paragraphs])

        name = doc.paragraphs[0].text.strip() if doc.paragraphs else "Untitled Recipe"

        ingredients = [self.clean_ingredient_text(i)
                       for i in self.extract_ingredients_section(full_text)]

        # Directions
        lines = full_text.split("\n")
        directions = []
        in_directions = False
        for line in lines:
            clean = line.strip()
            if re.match(r"^(directions?|instructions?|steps?):?$", clean, re.IGNORECASE):
                in_directions = True
                continue
            if in_directions and clean:
                directions.append(clean)

        self.recipe_data = {
            "name": name,
            "ingredients": ingredients,
            "directions": directions,
            "source_file": self.filepath,
            "format": "docx",
        }

        return self.recipe_data


# ======================================================================
#                        DEMO / MAIN USAGE
# ======================================================================

def demo_recipe_parsers():
    """Showcase all parser types working with inheritance & polymorphism."""

    print("=== Demo: TXT Parser ===")
    txt = TXTRecipeParser("data/sample_recipes/pasta_marinara.txt")
    if txt.validate_format():
        r = txt.parse()
        print("Parsed:", r["name"])

    print("\n=== Demo: PDF Parser ===")
    pdf = PDFRecipeParser("data/sample_recipes/chicken_stir_fry.pdf")
    if pdf.validate_format():
        r = pdf.parse()
        print("Parsed:", r["name"])

    print("\n=== Polymorphism Demo ===")
    for parser in [txt, pdf]:
        print(f"{parser.get_recipe_name()} ({parser.recipe_data.get('format')})")


def usage_in_main_project():
    """Example how the main DDM grocery system could consume the parsers."""
    print("\n=== Integration Example ===")

    recipe_files = [
        "data/sample_recipes/pasta_marinara.txt",
        "data/sample_recipes/chicken_stir_fry.pdf",
    ]

    recipes = []

    for filepath in recipe_files:
        if filepath.endswith(".txt"):
            parser = TXTRecipeParser(filepath)
        elif filepath.endswith(".pdf"):
            parser = PDFRecipeParser(filepath)
        elif filepath.endswith(".docx"):
            parser = DOCXRecipeParser(filepath)
        else:
            print("Unsupported format:", filepath)
            continue

        if parser.validate_format():
            recipes.append(parser.parse())
            print("✓ Parsed:", parser.get_recipe_name())
        else:
            print("✗ Failed:", filepath)

    print("\nTotal Recipes:", len(recipes))


if __name__ == "__main__":
    demo_recipe_parsers()
    usage_in_main_project()
