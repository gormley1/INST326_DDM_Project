from abc import ABC, abstractmethod

class BaseRecipe(ABC):
    """
    Basic recipe model for our grocery project.
    This is abstract, so we don't make objects directly from this.
    """

    def __init__(self, name: str, ingredients: list, servings: int):
        # just storing the main stuff we care about
        self.name = name
        self.ingredients = ingredients  # list of ingredient dicts or strings
        self.servings = servings

    @abstractmethod
    def get_scaled_ingredients(self, target_servings: int):
        """
        Each recipe type has to explain how to scale its ingredients.
        This is the rule every child class has to follow.
        """
        pass


class TextRecipe(BaseRecipe):
    """
    Recipe that originally came from a .txt file.
    """

    def __init__(self, name: str, ingredients: list, servings: int, source_path: str):
        super().__init__(name, ingredients, servings)
        self.source_path = source_path  # just so we know where it came from

    def get_scaled_ingredients(self, target_servings: int):
        """
        Super simple scaling: multiply quantity by a ratio.
        Assumes each ingredient dict has a 'quantity' key.
        """
        if self.servings == 0:
            return self.ingredients  # avoid dividing by zero

        ratio = target_servings / self.servings
        scaled = []

        for item in self.ingredients:
            new_item = item.copy()

            if "quantity" in new_item and isinstance(new_item["quantity"], (int, float)):
                new_item["quantity"] = new_item["quantity"] * ratio

            scaled.append(new_item)

        return scaled


class PdfRecipe(BaseRecipe):
    """
    Recipe that originally came from a .pdf file.
    Right now it scales almost the same way as TextRecipe,
    but we still override to show polymorphism.
    """

    def __init__(self, name: str, ingredients: list, servings: int, source_path: str):
        super().__init__(name, ingredients, servings)
        self.source_path = source_path

    def get_scaled_ingredients(self, target_servings: int):
        if self.servings == 0:
            return self.ingredients

        ratio = target_servings / self.servings
        scaled = []

        for item in self.ingredients:
            new_item = item.copy()

            if "quantity" in new_item and isinstance(new_item["quantity"], (int, float)):
                new_item["quantity"] = new_item["quantity"] * ratio

            scaled.append(new_item)

        return scaled


import csv

class CsvShoppingListExporter:
    """
    Small helper class that knows how to save a shopping list to a csv file.
    This keeps the file-writing logic in one place.
    """

    def __init__(self, shopping_list: dict):
        # shopping_list should be the same type of dict that compile_shopping_list returns
        self.shopping_list = shopping_list

    def export(self, filepath: str):
        """
        Writes the shopping list to a csv file.
        The csv will have one row per grocery item.
        """
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["item", "quantity", "unit", "recipes"])

            # Example of shopping_list format:
            # {
            #   "tomato": {"quantity": 6, "unit": "count", "recipes": ["Pasta"]}
            # }
            for item_name, info in self.shopping_list.items():
                quantity = info.get("quantity", "")
                unit = info.get("unit", "")
                recipes = ", ".join(info.get("recipes", []))
                writer.writerow([item_name, quantity, unit, recipes])


class ShoppingSession:
    """
    A full shopping session for the user.

    This class HAS recipes and HAS an exporter object.
    It is not a type of exporter, so this is a good example of composition
    instead of inheritance.
    """

    def __init__(self, recipes: list, shopping_list: dict):
        # list of BaseRecipe child objects (TextRecipe, PdfRecipe, etc.)
        self.recipes = recipes
        # shopping_list is the combined grocery list dict
        self.shopping_list = shopping_list
        # this class "has" an exporter and uses it when we want to save
        self.exporter = CsvShoppingListExporter(self.shopping_list)

    def add_recipe(self, recipe: BaseRecipe):
        """
        Add another recipe into this session.
        """
        self.recipes.append(recipe)

    def save_shopping_list(self, filepath: str):
        """
        Use the exporter object we already have to save the list.
        """
        self.exporter.export(filepath)
