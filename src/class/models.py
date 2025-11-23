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
