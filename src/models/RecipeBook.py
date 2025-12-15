"""
RecipeBook - Persistent storage for user's recipe collection.

This module provides the RecipeBook class for managing a user's recipe library
with JSON-based persistence. Recipes are saved to disk and loaded automatically
across program sessions.

DATA ARCHITECTURE:
The default storage path uses a nested user directory structure:
    data/users/test_user/recipe_book.json

This allows for future multi-user support. To add a new user:
    book = RecipeBook("data/users/john_doe/recipe_book.json")

Currently, the project operates with a single monolithic test user.

Author: DDM Team - Matthew Gormley (Data Architect)
Course: INST326 - Object-Oriented Programming for Information Science
Date: December 2024
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class RecipeBook:
    """
    Persistent storage manager for user's recipe collection.
    
    The RecipeBook class provides functionality to store, retrieve, and manage
    recipes with automatic JSON-based persistence. All changes are immediately
    saved to disk, which ensures data is not lost between program sessions.
    
    Attributes:
        filepath (Path): Path to the JSON storage file
        recipes (List[Dict]): List of recipe dictionaries
    
    Example:
        >>> book = RecipeBook("data/users/john_doe/my_recipes.json")
        >>> recipe = {
        ...     'name': 'Pasta Marinara',
        ...     'ingredients': ['1 lb pasta', '2 cans tomato paste'],
        ...     'directions': 'Boil pasta, make sauce, combine.'
        ... }
        >>> book.add_recipe(recipe)
        >>> retrieved = book.get_recipe('Pasta Marinara')
        >>> print(retrieved['name'])
        Pasta Marinara
    """
    
    def __init__(self, filepath: str = "data/users/test_user/recipe_book.json"):
        """
        Initialize RecipeBook with persistent storage.
        
        Creates the storage file and parent directories if they don't exist.
        Loads existing recipes from file if available.
        
        Args:
            filepath (str): Path to JSON storage file. 
                Defaults to 'data/users/test_user/recipe_book.json'
        
        Raises:
            IOError: If unable to create storage directory or file
        
        Note:
            The nested user directory structure (data/users/test_user/) allows for
            future multi-user support. Currently operates as single test user.
        """
        self.filepath = Path(filepath)
        self.recipes = self._load()
    
    def add_recipe(self, recipe: Dict) -> None:
        """
        Add a recipe to the collection and save to disk.
        
        Args:
            recipe (Dict): Recipe dictionary containing at minimum:
                - 'name' (str): Recipe name
                - 'ingredients' (List[str]): List of ingredient strings
                - 'directions' (str): Cooking directions
        
        Raises:
            ValueError: If recipe with same name already exists
            TypeError: If recipe is not a dictionary
            KeyError: If recipe missing required fields ('name', 'ingredients', 'directions')
        
        Example:
            >>> book = RecipeBook()
            >>> recipe = {
            ...     'name': 'Chocolate Chip Cookies',
            ...     'ingredients': ['2 cups flour', '1 cup sugar', '2 eggs'],
            ...     'directions': 'Mix ingredients. Bake at 350°F for 12 minutes.'
            ... }
            >>> book.add_recipe(recipe)
        """
        # Validate input
        if not isinstance(recipe, dict):
            raise TypeError("Recipe must be a dictionary")
        
        required_fields = ['name', 'ingredients', 'directions']
        for field in required_fields:
            if field not in recipe:
                raise KeyError(f"Recipe missing required field: '{field}'")
        
        # Check for duplicates
        if any(r['name'].lower() == recipe['name'].lower() for r in self.recipes):
            raise ValueError(f"Recipe '{recipe['name']}' already exists in recipe book")
        
        # Initialize tags as empty list if not provided
        if 'tags' not in recipe:
            recipe['tags'] = []
        
        # Add timestamp
        recipe['date_added'] = datetime.now().isoformat()
        
        # Add to collection and save
        self.recipes.append(recipe)
        self._save()
    
    def get_recipe(self, name: str) -> Optional[Dict]:
        """
        Retrieve a recipe by name (case-insensitive).
        
        Args:
            name (str): Name of recipe to retrieve
        
        Returns:
            Dict or None: Recipe dictionary if found, None if not found
        
        Example:
            >>> book = RecipeBook()
            >>> recipe = book.get_recipe('Pasta Marinara')
            >>> if recipe:
            ...     print(recipe['name'])
            Pasta Marinara
        """
        if not isinstance(name, str):
            raise TypeError("Recipe name must be a string")
        
        for recipe in self.recipes:
            if recipe['name'].lower() == name.lower():
                return recipe.copy()  # Return copy to prevent external modification
        
        return None
    
    def list_recipes(self) -> List[Dict]:
        """
        Return list of all recipes in the collection.
        
        Returns:
            List[Dict]: List of all recipe dictionaries (copies)
        
        Example:
            >>> book = RecipeBook()
            >>> recipes = book.list_recipes()
            >>> for recipe in recipes:
            ...     print(recipe['name'])
            Pasta Marinara
            Chocolate Chip Cookies
            Caesar Salad
        """
        # Return copies to prevent external modification
        return [recipe.copy() for recipe in self.recipes]
    
    def list_recipe_names(self) -> List[str]:
        """
        Return list of recipe names only.
        
        Convenient method for displaying recipe options to users.
        
        Returns:
            List[str]: List of recipe names
        
        Example:
            >>> book = RecipeBook()
            >>> names = book.list_recipe_names()
            >>> print(names)
            ['Pasta Marinara', 'Chocolate Chip Cookies', 'Caesar Salad']
        """
        return [recipe['name'] for recipe in self.recipes]
    
    def remove_recipe(self, name: str) -> bool:
        """
        Remove a recipe by name and save changes.
        
        Args:
            name (str): Name of recipe to remove (case-insensitive)
        
        Returns:
            bool: True if recipe was removed, False if not found
        
        Example:
            >>> book = RecipeBook()
            >>> book.remove_recipe('Pasta Marinara')
            True
            >>> book.remove_recipe('Nonexistent Recipe')
            False
        """
        if not isinstance(name, str):
            raise TypeError("Recipe name must be a string")
        
        original_len = len(self.recipes)
        self.recipes = [
            r for r in self.recipes 
            if r['name'].lower() != name.lower()
        ]
        
        if len(self.recipes) < original_len:
            self._save()
            return True
        
        return False
    
    def update_recipe(self, name: str, updated_recipe: Dict) -> bool:
        """
        Update an existing recipe.
        
        Args:
            name (str): Name of recipe to update
            updated_recipe (Dict): Updated recipe data
        
        Returns:
            bool: True if updated, False if recipe not found
        
        Raises:
            TypeError: If updated_recipe is not a dictionary
            KeyError: If updated_recipe missing required fields
        
        Example:
            >>> book = RecipeBook()
            >>> updated = {
            ...     'name': 'Pasta Marinara',
            ...     'ingredients': ['1 lb pasta', '3 cans tomato paste'],  # Changed amount
            ...     'directions': 'Boil pasta, make sauce, combine.'
            ... }
            >>> book.update_recipe('Pasta Marinara', updated)
            True
        """
        # Validate input
        if not isinstance(updated_recipe, dict):
            raise TypeError("Updated recipe must be a dictionary")
        
        required_fields = ['name', 'ingredients', 'directions']
        for field in required_fields:
            if field not in updated_recipe:
                raise KeyError(f"Recipe missing required field: '{field}'")
        
        # Find and update recipe
        for i, recipe in enumerate(self.recipes):
            if recipe['name'].lower() == name.lower():
                # Preserve date_added if it exists
                if 'date_added' in recipe:
                    updated_recipe['date_added'] = recipe['date_added']
                
                # Add update timestamp
                updated_recipe['date_updated'] = datetime.now().isoformat()
                
                self.recipes[i] = updated_recipe
                self._save()
                return True
        
        return False
    
    def search_recipes(self, keyword: str) -> List[Dict]:
        """
        Search recipes by keyword in name or ingredients.
        
        Args:
            keyword (str): Search term (case-insensitive)
        
        Returns:
            List[Dict]: List of matching recipes
        
        Example:
            >>> book = RecipeBook()
            >>> results = book.search_recipes('pasta')
            >>> for recipe in results:
            ...     print(recipe['name'])
            Pasta Marinara
            Pasta Alfredo
        """
        if not isinstance(keyword, str):
            raise TypeError("Search keyword must be a string")
        
        keyword_lower = keyword.lower()
        results = []
        
        for recipe in self.recipes:
            # Check name
            if keyword_lower in recipe['name'].lower():
                results.append(recipe.copy())
                continue
            
            # Check ingredients
            ingredients_text = ' '.join(recipe['ingredients']).lower()
            if keyword_lower in ingredients_text:
                results.append(recipe.copy())
        
        return results
    
    def count_recipes(self) -> int:
        """
        Return the number of recipes in the collection.
        
        Returns:
            int: Number of recipes
        
        Example:
            >>> book = RecipeBook()
            >>> print(f"You have {book.count_recipes()} recipes")
            You have 5 recipes
        """
        return len(self.recipes)
    
    def clear_all(self) -> None:
        """
        Remove all recipes from the collection.
        
        Warning: This action cannot be undone!
        
        Example:
            >>> book = RecipeBook()
            >>> book.clear_all()
            >>> book.count_recipes()
            0
        """
        self.recipes = []
        self._save()
    
    def add_tag_to_recipe(self, recipe_name: str, tag: str) -> bool:
        """
        Add a tag to a specific recipe.
        
        Tags are used to categorize recipes (e.g., "dinner", "dessert", "quick", "crockpot", "party appetizers", "drinks", etc).
        Tags are case-insensitive and stored in lowercase.
        
        Args:
            recipe_name (str): Name of recipe to tag
            tag (str): Tag to add (e.g., "dinner", "crock pot")
        
        Returns:
            bool: True if tag added, False if recipe not found
        
        Example:
            >>> book = RecipeBook()
            >>> book.add_tag_to_recipe('Pasta Marinara', 'dinner')
            True
            >>> book.add_tag_to_recipe('Pasta Marinara', 'italian')
            True
        """
        if not isinstance(tag, str):
            raise TypeError("Tag must be a string")
        
        # Normalize tag to lowercase
        tag = tag.lower().strip()
        
        if not tag:
            raise ValueError("Tag cannot be empty")
        
        # Find recipe
        for recipe in self.recipes:
            if recipe['name'].lower() == recipe_name.lower():
                # Initialize tags list if doesn't exist
                if 'tags' not in recipe:
                    recipe['tags'] = []
                
                # Add tag if not already present
                if tag not in recipe['tags']:
                    recipe['tags'].append(tag)
                    self._save()
                
                return True
        
        return False
    
    def remove_tag_from_recipe(self, recipe_name: str, tag: str) -> bool:
        """
        Remove a tag from a specific recipe.
        
        Args:
            recipe_name (str): Name of recipe
            tag (str): Tag to remove
        
        Returns:
            bool: True if tag removed, False if recipe not found or tag not present
        
        Example:
            >>> book = RecipeBook()
            >>> book.remove_tag_from_recipe('Pasta Marinara', 'dinner')
            True
        """
        if not isinstance(tag, str):
            raise TypeError("Tag must be a string")
        
        tag = tag.lower().strip()
        
        # Find recipe
        for recipe in self.recipes:
            if recipe['name'].lower() == recipe_name.lower():
                if 'tags' in recipe and tag in recipe['tags']:
                    recipe['tags'].remove(tag)
                    self._save()
                    return True
                return False
        
        return False
    
    def get_all_tags(self) -> List[str]:
        """
        Get list of all unique tags across all recipes.
        
        Useful for showing users available tag options when categorizing recipes.
        
        Returns:
            List[str]: Sorted list of unique tags
        
        Example:
            >>> book = RecipeBook()
            >>> tags = book.get_all_tags()
            >>> print(tags)
            ['appetizer', 'dessert', 'dinner', 'italian', 'quick', 'vegetarian']
        """
        all_tags = set()
        
        for recipe in self.recipes:
            if 'tags' in recipe:
                all_tags.update(recipe['tags'])
        
        return sorted(list(all_tags))
    
    def get_tag_counts(self) -> Dict[str, int]:
        """
        Get dictionary of tags with count of recipes using each tag.
        
        Returns:
            Dict[str, int]: Tag names mapped to usage counts
        
        Example:
            >>> book = RecipeBook()
            >>> counts = book.get_tag_counts()
            >>> print(counts)
            {'dinner': 5, 'dessert': 3, 'quick': 7, 'italian': 2}
        """
        tag_counts = {}
        
        for recipe in self.recipes:
            if 'tags' in recipe:
                for tag in recipe['tags']:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return dict(sorted(tag_counts.items()))
    
    def search_by_tag(self, tag: str) -> List[Dict]:
        """
        Find all recipes with a specific tag.
        
        Args:
            tag (str): Tag to search for (case-insensitive)
        
        Returns:
            List[Dict]: List of recipes with that tag
        
        Example:
            >>> book = RecipeBook()
            >>> dinner_recipes = book.search_by_tag('dinner')
            >>> for recipe in dinner_recipes:
            ...     print(recipe['name'])
            Pasta Marinara
            Chicken Stir Fry
            Beef Tacos
        """
        if not isinstance(tag, str):
            raise TypeError("Tag must be a string")
        
        tag = tag.lower().strip()
        results = []
        
        for recipe in self.recipes:
            if 'tags' in recipe and tag in recipe['tags']:
                results.append(recipe.copy())
        
        return results
    
    def search_by_multiple_tags(self, tags: List[str], match_all: bool = False) -> List[Dict]:
        """
        Find recipes matching one or more tags.
        
        Args:
            tags (List[str]): List of tags to search for
            match_all (bool): If True, recipe must have ALL tags. If False, ANY tag matches.
        
        Returns:
            List[Dict]: Matching recipes
        
        Example:
            >>> book = RecipeBook()
            >>> # Find recipes that are BOTH dinner AND quick
            >>> recipes = book.search_by_multiple_tags(['dinner', 'quick'], match_all=True)
            >>> 
            >>> # Find recipes that are EITHER italian OR mexican
            >>> recipes = book.search_by_multiple_tags(['italian', 'mexican'], match_all=False)
        """
        if not isinstance(tags, list):
            raise TypeError("Tags must be a list")
        
        # Normalize tags
        search_tags = [tag.lower().strip() for tag in tags]
        results = []
        
        for recipe in self.recipes:
            recipe_tags = recipe.get('tags', [])
            
            if match_all:
                # Recipe must have ALL tags
                if all(tag in recipe_tags for tag in search_tags):
                    results.append(recipe.copy())
            else:
                # Recipe must have AT LEAST ONE tag
                if any(tag in recipe_tags for tag in search_tags):
                    results.append(recipe.copy())
        
        return results
    
    def get_recipes_by_tag(self) -> Dict[str, List[str]]:
        """
        Organize recipe names by tag (like Chrome tab groups!).
        
        Returns a dictionary where each tag maps to a list of recipe names.
        
        Returns:
            Dict[str, List[str]]: Tags mapped to recipe names
        
        Example:
            >>> book = RecipeBook()
            >>> organized = book.get_recipes_by_tag()
            >>> print(organized)
            {
                'dinner': ['Pasta Marinara', 'Chicken Stir Fry', 'Beef Tacos'],
                'dessert': ['Chocolate Cake', 'Apple Pie'],
                'quick': ['Pasta Marinara', 'Caesar Salad']
            }
        """
        tag_groups = {}
        
        for recipe in self.recipes:
            recipe_tags = recipe.get('tags', [])
            for tag in recipe_tags:
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(recipe['name'])
        
        return dict(sorted(tag_groups.items()))
    
    def _load(self) -> List[Dict]:
        """
        Load recipes from JSON file.
        
        Creates an empty recipe book if file doesn't exist or is corrupted.
        
        Returns:
            List[Dict]: List of recipes loaded from file
        """
        # Create parent directory if it doesn't exist
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # If file doesn't exist, create empty one
        if not self.filepath.exists():
            self._save_to_file([])
            return []
        
        # Try to load existing file
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Validate data structure
                if not isinstance(data, list):
                    print(f"Warning: Invalid recipe book format. Starting fresh.")
                    return []
                
                return data
        
        except json.JSONDecodeError:
            print(f"Warning: Could not read {self.filepath}. File may be corrupted. Starting fresh.")
            return []
        
        except IOError as e:
            print(f"Warning: Error reading {self.filepath}: {e}. Starting fresh.")
            return []
    
    def _save(self) -> None:
        """
        Save current recipes to JSON file.
        
        Raises:
            IOError: If unable to write to file
        """
        self._save_to_file(self.recipes)
    
    def _save_to_file(self, data: List[Dict]) -> None:
        """
        Write data to JSON file with error handling.
        
        Args:
            data (List[Dict]): Recipe data to save
        
        Raises:
            IOError: If unable to write to file
        """
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except IOError as e:
            raise IOError(f"Error saving recipe book to {self.filepath}: {e}")
    
    def export_to_json(self, filepath: str) -> None:
        """
        Export recipe book to a different JSON file.
        
        Useful for creating backups or sharing recipe collections.
        
        Args:
            filepath (str): Destination file path
        
        Example:
            >>> book = RecipeBook()
            >>> book.export_to_json('backup/recipes_backup.json')
        """
        export_path = Path(filepath)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.recipes, f, indent=2, ensure_ascii=False)
        
        except IOError as e:
            raise IOError(f"Error exporting to {filepath}: {e}")
    
    def import_from_json(self, filepath: str, merge: bool = False) -> int:
        """
        Import recipes from a JSON file.
        
        Args:
            filepath (str): Path to JSON file containing recipes
            merge (bool): If True, merge with existing recipes. If False, replace all.
        
        Returns:
            int: Number of recipes imported
        
        Raises:
            FileNotFoundError: If import file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        
        Example:
            >>> book = RecipeBook()
            >>> count = book.import_from_json('shared_recipes.json', merge=True)
            >>> print(f"Imported {count} recipes")
            Imported 5 recipes
        """
        import_path = Path(filepath)
        
        if not import_path.exists():
            raise FileNotFoundError(f"Import file not found: {filepath}")
        
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_recipes = json.load(f)
            
            if not isinstance(imported_recipes, list):
                raise ValueError("Import file must contain a list of recipes")
            
            if merge:
                # Add only new recipes (avoid duplicates)
                existing_names = {r['name'].lower() for r in self.recipes}
                new_recipes = [
                    r for r in imported_recipes 
                    if r['name'].lower() not in existing_names
                ]
                self.recipes.extend(new_recipes)
                count = len(new_recipes)
            else:
                # Replace all recipes
                self.recipes = imported_recipes
                count = len(imported_recipes)
            
            self._save()
            return count
        
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in import file: {e}", e.doc, e.pos)
    
    def __repr__(self) -> str:
        """String representation of RecipeBook."""
        return f"RecipeBook(filepath='{self.filepath}', recipes={len(self.recipes)})"
    
    def __len__(self) -> int:
        """Allow len(recipe_book) to return number of recipes."""
        return len(self.recipes)
    
    def __contains__(self, name: str) -> bool:
        """
        Allow 'recipe_name' in recipe_book syntax.
        
        Example:
            >>> book = RecipeBook()
            >>> 'Pasta Marinara' in book
            True
        """
        return any(r['name'].lower() == name.lower() for r in self.recipes)


# Example usage and testing
if __name__ == "__main__":
    # Create a recipe book (uses default path: data/users/test_user/recipe_book.json)
    book = RecipeBook()
    
    # Add some test recipes WITH TAGS
    test_recipes = [
        {
            'name': 'Pasta Marinara',
            'ingredients': [
                '1 lb pasta',
                '2 cans (6 oz) tomato paste',
                '3 cloves garlic, minced',
                '1 tsp dried basil',
                '1 tsp dried oregano',
                'Salt and pepper to taste'
            ],
            'directions': 'Boil pasta according to package directions. Meanwhile, sauté garlic in olive oil, add tomato paste and seasonings. Simmer 10 minutes. Combine with cooked pasta.',
            'tags': ['dinner', 'italian', 'vegetarian', 'quick']
        },
        {
            'name': 'Caesar Salad',
            'ingredients': [
                '1 head romaine lettuce',
                '1/2 cup parmesan cheese',
                '1 cup croutons',
                '1/2 cup Caesar dressing'
            ],
            'directions': 'Chop lettuce. Toss with dressing, cheese, and croutons. Serve immediately.',
            'tags': ['salad', 'side dish', 'quick']
        },
        {
            'name': 'Chocolate Chip Cookies',
            'ingredients': [
                '2 cups all-purpose flour',
                '1 cup butter, softened',
                '3/4 cup granulated sugar',
                '3/4 cup brown sugar',
                '2 eggs',
                '2 cups chocolate chips',
                '1 tsp vanilla extract',
                '1 tsp baking soda',
                '1/2 tsp salt'
            ],
            'directions': 'Cream butter and sugars. Add eggs and vanilla. Mix in dry ingredients. Fold in chocolate chips. Drop by spoonfuls onto baking sheet. Bake at 350°F for 10-12 minutes.',
            'tags': ['dessert', 'baking', 'party']
        }
    ]
    
    print("Adding test recipes...")
    for recipe in test_recipes:
        try:
            book.add_recipe(recipe)
            print(f"✓ Added: {recipe['name']} (tags: {', '.join(recipe['tags'])})")
        except ValueError as e:
            print(f"✗ {e}")
    
    print(f"\nTotal recipes: {book.count_recipes()}")
    print(f"\nRecipe names: {book.list_recipe_names()}")
    
    # Test retrieval
    print("\n--- Testing Retrieval ---")
    pasta = book.get_recipe('Pasta Marinara')
    if pasta:
        print(f"Found: {pasta['name']}")
        print(f"Tags: {', '.join(pasta['tags'])}")
        print(f"Ingredients: {len(pasta['ingredients'])} items")
    
    # Test tag features
    print("\n--- Testing Tag Features ---")
    
    # Get all tags
    all_tags = book.get_all_tags()
    print(f"\nAll tags in recipe book: {all_tags}")
    
    # Get tag counts
    tag_counts = book.get_tag_counts()
    print("\nTag usage counts:")
    for tag, count in tag_counts.items():
        print(f"  {tag}: {count} recipe(s)")
    
    # Search by tag
    print("\n--- Searching by Tag ---")
    quick_recipes = book.search_by_tag('quick')
    print(f"Recipes tagged 'quick': {len(quick_recipes)}")
    for recipe in quick_recipes:
        print(f"  - {recipe['name']}")
    
    # Add tag to existing recipe
    print("\n--- Adding Tag to Recipe ---")
    book.add_tag_to_recipe('Chocolate Chip Cookies', 'kid-friendly')
    cookies = book.get_recipe('Chocolate Chip Cookies')
    print(f"Updated tags for Cookies: {cookies['tags']}")
    
    # Get recipes organized by tag (like Chrome tab groups!)
    print("\n--- Recipes Organized by Tag (Chrome-style groups) ---")
    tag_groups = book.get_recipes_by_tag()
    for tag, recipe_names in tag_groups.items():
        print(f"\n📁 {tag.upper()}")
        for name in recipe_names:
            print(f"   - {name}")
    
    # Search with multiple tags
    print("\n--- Multi-Tag Search ---")
    print("Recipes that are BOTH 'dinner' AND 'quick':")
    results = book.search_by_multiple_tags(['dinner', 'quick'], match_all=True)
    for recipe in results:
        print(f"  - {recipe['name']}")
    
    print("\n--- Testing Membership ---")
    print(f"'Caesar Salad' in book: {'Caesar Salad' in book}")
    print(f"'Pizza' in book: {'Pizza' in book}")
    
    print(f"\n{book}")
    print("\n✓ RecipeBook test complete!")