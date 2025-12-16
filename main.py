"""
Cornucopia Grocery List Assistant - Main CLI Application

A comprehensive tool for importing recipes, planning meals, comparing grocery
store prices, and generating optimized shopping lists.

Team DDM - INST326 Project
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.RecipeBook import RecipeBook
from src.export_utils import export_to_csv, export_to_pdf, export_to_txt, group_items_by_category
from src.recipe_parser import RecipeParser, TXTRecipeParser, PDFRecipeParser, DOCXRecipeParser
from src.shopping_list import compile_shopping_list
from src.store_data import compare_store_totals


class CornucopiaApp:
    """Main application class for Cornucopia Grocery Assistant."""
    
    def __init__(self, username: str = "test_user"):
        """Initialize the application.
        
        Args:
            username: User identifier for data storage
        """
        self.username = username
        self.user_dir = os.path.join("data", "users", username)
        os.makedirs(self.user_dir, exist_ok=True)
        
        # Initialize RecipeBook
        self.recipe_book = RecipeBook(username)
        
        # Session state
        self.current_shopping_list = None
        self.shopping_history: List[Dict] = []  # Last 5 lists
        
        # Load settings
        self.settings = self.load_settings()
        
    def load_settings(self) -> Dict:
        """Load user settings or create defaults.
        
        Returns:
            Settings dictionary
        """
        settings_file = os.path.join(self.user_dir, "settings.json")
        
        default_settings = {
            "default_servings": 4,
            "preferred_stores": ["safeway", "giant", "trader_joes"],
            "default_export_format": "pdf",
            "export_directory": "exports"
        }
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return default_settings
        
        return default_settings
    
    def save_settings(self) -> None:
        """Save current settings to file."""
        settings_file = os.path.join(self.user_dir, "settings.json")
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, indent=2, fp=f)
            print("Settings saved successfully!")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def run(self) -> None:
        """Main application loop."""
        self.print_welcome()
        
        while True:
            self.print_main_menu()
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                self.import_recipe_workflow()
            elif choice == '2':
                self.view_recipe_book_workflow()
            elif choice == '3':
                self.create_shopping_list_workflow()
            elif choice == '4':
                self.compare_prices_workflow()
            elif choice == '5':
                self.export_shopping_list_workflow()
            elif choice == '6':
                self.settings_workflow()
            elif choice == '7':
                self.exit_application()
                break
            else:
                print("\nInvalid choice. Please enter 1-7.")
            
            input("\nPress Enter to continue...")
    
    def print_welcome(self) -> None:
        """Print welcome banner."""
        print("\n" + "="*60)
        print(" CORNUCOPIA GROCERY ASSISTANT ")
        print("="*60)
        print("\n  Smart meal planning & grocery shopping made easy!")
        print(f"  User: {self.username}")
        print("="*60 + "\n")
    
    def print_main_menu(self) -> None:
        """Print main menu options."""
        print("\n" + "─"*60)
        print("MAIN MENU")
        print("─"*60)
        print("1. Import Recipe")
        print("2. View Recipe Book")
        print("3. Create Shopping List")
        print("4. Compare Store Prices")
        print("5. Export Shopping List")
        print("6. Settings")
        print("7. Exit")
        print("─"*60)
    
    # ═══════════════════════════════════════════════════════════════
    # IMPORT RECIPE
    # ═══════════════════════════════════════════════════════════════
    
    def import_recipe_workflow(self) -> None:
        """Handle recipe import workflow w/ rename and preview."""
        print("\n" + "="*60)
        print("IMPORT RECIPE")
        print("="*60)
        
        # Get file path
        filepath = input("\nEnter recipe file path: ").strip()
        
        if not filepath:
            print("No file path provided.")
            return
        
        # Parse recipe
        try:
            print(f"\nParsing recipe from: {filepath}")
            # Determine parser type based on file extension
            if filepath.endswith('.txt'):
                parser = TXTRecipeParser(filepath)
            elif filepath.endswith('.pdf'):
                parser = PDFRecipeParser(filepath)
            elif filepath.endswith('.docx'):
                parser = DOCXRecipeParser(filepath)
            else:
                raise ValueError(f"Unsupported file format. Supported: .txt, .pdf, .docx")
                return

            # Validate format and parse
            if not parser.validate_format():
                print("Invalid file format")
                return
            else: # parse the recipe
                recipe = parser.parse()
                print(f"Successfully parsed: {recipe['name']}")
            
            # ----- added during bug fixes: offer to rename recipe file -----
            print(f"\nParsed recipe name: '{recipe['name']}'")
            rename = input("Rename this recipe? (y/n) : ").strip().lower()

            if rename == 'y':
                new_name = input("Enter new recipe name: ").strip()
                if new_name:
                    old_name = recipe['name']
                    recipe['name'] = new_name
                    print(f"Recipe renamed: '{old_name}' --> '{new_name}'")
            # ---------------------------------------------------------------

            # ----- added during bug fixes: show recipe preview -----
            print(f"\n{'─'*60}")
            print("RECIPE PREVIEW")
            print("─"*60)
            print(f"Name: {recipe['name']}")
            print(f"Format: {recipe.get('format', 'unknown')}")
            print(f"\nIngredients ({len(recipe['ingredients'])} items):")
        
            if recipe['ingredients']:
                # Show first 3 ingredients
                for i, ingredient in enumerate(recipe['ingredients'][:3], 1):
                    print(f"  {i}. {ingredient}")
            
                # Show count of remaining
                if len(recipe['ingredients']) > 3:
                    remaining = len(recipe['ingredients']) - 3
                    print(f"  ... and {remaining} more")
            else:
                print("     Warning: No ingredients found!")
        
            print(f"\nDirections preview:")
            directions = recipe['directions']
            if isinstance(directions, list):
                print(f"  {len(directions)} steps")
                if directions:
                    print(f"  1. {directions[0][:80]}...")
            else:
                preview = directions[:100] if len(directions) > 100 else directions
                print(f"  {preview}...")
            # -------------------------------------------------------

            # ----- added during bug fixes: confirmation -----
            print(f"\n{'-'*60}")
            confirm = input("Import this recipe? (y/n) : ").strip().lower()
            if confirm == 'n':
                print("Recipe import cancelled.")
                return
            # ------------------------------------------------
            
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return
        except Exception as e:
            print(f"Error parsing recipe: {e}")
            return
        
        # Show existing tags
        all_tags = self.recipe_book.get_all_tags()
        if all_tags:
            print(f"\nExisting tags: {', '.join(sorted(all_tags))}")
        
        # Add tags
        print("\nAdd tags to this recipe (comma-separated, or press Enter to skip):")
        tag_input = input("Tags: ").strip()
        
        if tag_input:
            tags = [tag.strip() for tag in tag_input.split(',') if tag.strip()]
            recipe['tags'] = tags
        else:
            recipe['tags'] = []
        
        # Save to recipe book
        try:
            self.recipe_book.add_recipe(recipe)
            print(f"\nRecipe '{recipe['name']}' added to your recipe book!")
            if recipe['tags']:
                print(f"  Tags: {', '.join(recipe['tags'])}")
        except Exception as e:
            print(f"Error saving recipe: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # VIEW RECIPE BOOK
    # ═══════════════════════════════════════════════════════════════
    
    def view_recipe_book_workflow(self) -> None:
        """Handle recipe book viewing and tag management."""
        while True:
            print("\n" + "="*60)
            print("VIEW RECIPE BOOK")
            print("="*60)
            print("\n1. List All Recipes")
            print("2. Filter by Tag")
            print("3. Search Recipes")
            print("4. View Recipe Details")
            print("5. Back to Main Menu")
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == '1':
                self.list_all_recipes()
            elif choice == '2':
                self.filter_recipes_by_tag()
            elif choice == '3':
                self.search_recipes()
            elif choice == '4':
                self.view_recipe_details()
            elif choice == '5':
                break
            else:
                print("Invalid choice.")
    
    def list_all_recipes(self) -> None:
        """List all recipes in the book."""
        recipe_names = self.recipe_book.list_recipe_names()  # Returns list of strings
    
        if not recipe_names:
            print("\nNo recipes in your book yet.")
            return
    
        print(f"\nAll Recipes ({len(recipe_names)}):")
        print("─"*60)
        for i, name in enumerate(recipe_names, 1):
            recipe = self.recipe_book.get_recipe(name)
            tags = recipe.get('tags', [])
            tag_str = f" [{', '.join(tags)}]" if tags else ""
            print(f"{i}. {name}{tag_str}")
    
    def filter_recipes_by_tag(self) -> None:
        """Filter and display recipes by tag."""
        all_tags = self.recipe_book.get_all_tags()
        
        if not all_tags:
            print("\nNo tags available. Add tags to recipes first.")
            return
        
        print("\nAvailable tags:")
        tags_list = sorted(all_tags)
        for i, tag in enumerate(tags_list, 1):
            count = len(self.recipe_book.search_by_tag(tag))
            print(f"{i}. {tag} ({count})")
        
        tag_input = input("\nEnter tag name or number: ").strip()
        
        # Handle numeric input
        if tag_input.isdigit():
            idx = int(tag_input) - 1
            if 0 <= idx < len(tags_list):
                tag = tags_list[idx]
            else:
                print("Invalid tag number.")
                return
        else:
            tag = tag_input
        
        # Get recipes with tag
        recipes = self.recipe_book.search_by_tag(tag)
        
        if not recipes:
            print(f"\nNo recipes found with tag '{tag}'.")
            return
        
        print(f"\nRecipes tagged '{tag}' ({len(recipes)}):")
        print("─"*60)
        for i, recipe in enumerate(recipes, 1):
            other_tags = [t for t in recipe.get('tags', []) if t != tag]
            tag_str = f" [{', '.join(other_tags)}]" if other_tags else ""
            print(f"{i}. {recipe['name']}{tag_str}")
    
    def search_recipes(self) -> None:
        """Search recipes by keyword."""
        keyword = input("\nEnter search keyword: ").strip()
        
        if not keyword:
            print("No keyword provided.")
            return
        
        results = self.recipe_book.search_recipes(keyword)
        
        if not results:
            print(f"\nNo recipes found matching '{keyword}'.")
            return
        
        print(f"\nSearch results for '{keyword}' ({len(results)}):")
        print("─"*60)
        for i, recipe in enumerate(results, 1):
            tags = recipe.get('tags', [])
            tag_str = f" [{', '.join(tags)}]" if tags else ""
            print(f"{i}. {recipe['name']}{tag_str}")
    
    def view_recipe_details(self) -> None:
        """View detailed recipe information with tag management."""
        recipe_name = input("\nEnter recipe name: ").strip()
        
        if not recipe_name:
            print("No recipe name provided.")
            return
        
        try:
            recipe = self.recipe_book.get_recipe(recipe_name)
        except ValueError as e:
            print(f"Error: {e}")
            return
        
        # ------ added during bug fixes: fuzzy matching for partial name entry ------
        if recipe is None: # trying to find partial matches
            all_recipes = self.recipe_book.list_recipe_names()
            matches = [r for r in all_recipes if recipe_name.lower() in r.lower()]
            if not matches:
                print(f"Recupe '{recipe_name}' not found.")
                return
            elif len(matches) == 1: # only one match; use it
                recipe_name = matches[0]
                recipe = self.recipe_book.get_recipe(recipe_name)
                print(f"     Found: {recipe_name}")
            else: # multiple matches; let user choose
                print(f"\nMultiple matches found for '{recipe_name}':")
                for i, match in enumerate(matches, 1):
                    print(f"   {i}. {match}")
                selection = input("\nSelect recipe number: ").strip()

                try:
                    idx = int(selection) - 1
                    if 0 <= idx < len(matches):
                        recipe_name = matches[idx]
                        recipe = self.recipe_book.get_recipe(recipe_name)
                    else:
                        print("Invalid selection.")
                        return
                except ValueError:
                    print("Please enter a number.")
                    return
        # ---------------------------------------------------------------------------
        
        # Display recipe details
        print("\n" + "="*60)
        print(f"RECIPE: {recipe['name']}")
        print("="*60)
        
        # Tags
        tags = recipe.get('tags', [])
        if tags:
            print(f"\n   Tags: {', '.join(tags)}")
        else:
            print("\n   Tags: (none)")
        
        # Ingredients
        print(f"\nIngredients ({len(recipe['ingredients'])}):")
        for ingredient in recipe['ingredients']:
            print(f"  • {ingredient}")
        
        # Directions
        print(f"\nDirections:")
        directions = recipe['directions']
        if isinstance(directions, list):
            for i, step in enumerate(directions, 1):
                print(f"   {i}. {step}")
        else: # display as text (truncate if it's super long)
            if len(directions) > 200:
                print(f"  {directions[:200]}...")
            else:
                print(f"   {directions}")
        
        # Tag management
        print("\n" + "─"*60)
        print("Tag Management:")
        print("1. Add tag")
        print("2. Remove tag")
        print("3. Edit recipe")
        print("4. Delete this recipe")
        print("5. Done")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            new_tag = input("Enter tag to add: ").strip()
            if new_tag:
                try:
                    self.recipe_book.add_tag_to_recipe(recipe_name, new_tag)
                    print(f"Tag '{new_tag}' added to {recipe_name}")
                except Exception as e:
                    print(f"Error: {e}")
        
        elif choice == '2':
            if not tags:
                print("No tags to remove.")
                return
            
            print("\nCurrent tags:")
            for i, tag in enumerate(tags, 1):
                print(f"{i}. {tag}")
            
            tag_input = input("Enter tag name or number to remove: ").strip()
            
            # Handle numeric input
            if tag_input.isdigit():
                idx = int(tag_input) - 1
                if 0 <= idx < len(tags):
                    tag_to_remove = tags[idx]
                else:
                    print("Invalid tag number.")
                    return
            else:
                tag_to_remove = tag_input
            
            try:
                self.recipe_book.remove_tag_from_recipe(recipe_name, tag_to_remove)
                print(f"Tag '{tag_to_remove}' removed from {recipe_name}")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == '3': # added new recipe edit functionality in debugging
            self.edit_recipe_workflow(recipe_name, recipe)

        elif choice == '4': # added delete option in debugging
            print(f"   WARNING: This will permanently delete '{recipe_name}'")
            confirm = input("Are you sure? (yes/no): ").strip().lower()
            if confirm == 'yes':
                try: 
                    result = self.recipe_book.remove_recipe(recipe_name)
                    if result: 
                        print(f"Recpe '{recipe_name}' deleted successfully")
                    else:
                        print(f"Failed to delete recipe")
                except Exception as e:
                    print(f"Error deleting recipe: {e}")
            else:
                print("Deletion cancelled")

    def edit_recipe_workflow(self, recipe_name: str, recipe: Dict) -> None:
        """Interactive recipe editing workflow.
    
        Args:
          recipe_name: Current recipe name
            recipe: Recipe data dictionary
        """
        print("\n" + "="*60)
        print(f"EDIT RECIPE: {recipe_name}")
        print("="*60)
    
        while True:
            print("\nWhat would you like to edit?")
            print("1. Recipe name")
            print("2. Ingredients")
            print("3. Directions")
            print("4. Save and exit")
            print("5. Cancel (discard changes)")
        
            choice = input("\nEnter choice (1-5): ").strip()
        
            if choice == '1':
                # Edit recipe name
                print(f"\nCurrent name: {recipe['name']}")
                new_name = input("Enter new name (or press Enter to keep): ").strip()
            
                if new_name:
                    # Check if name already exists
                    if new_name != recipe_name and new_name in self.recipe_book:
                        print(f"Recipe '{new_name}' already exists")
                    else:
                        recipe['name'] = new_name
                        print(f"Name updated to: {new_name}")
        
            elif choice == '2':
                # Edit ingredients
                self.edit_ingredients(recipe)
        
            elif choice == '3':
                # Edit directions
                self.edit_directions(recipe)
        
            elif choice == '4':
                # Save changes
                try:
                    # Remove old recipe if name changed
                    if recipe['name'] != recipe_name:
                        self.recipe_book.remove_recipe(recipe_name)
                        self.recipe_book.add_recipe(recipe)
                        print(f"✓ Recipe saved as '{recipe['name']}'")
                    else:
                        self.recipe_book.update_recipe(recipe_name, recipe)
                        print(f"✓ Changes saved to '{recipe_name}'")
                    break
                except Exception as e:
                    print(f"✗ Error saving recipe: {e}")
        
            elif choice == '5':
                print("Changes discarded")
                break
        
            else:
                print("Invalid choice")


    def edit_ingredients(self, recipe: Dict) -> None:
        """Edit recipe ingredients interactively.
        
        Args:
            recipe: Recipe dictionary to modify
        """
        while True:
            print("\n" + "─"*40)
            print("EDIT INGREDIENTS")
            print("─"*40)
            print(f"Current ingredients ({len(recipe['ingredients'])}):")

            for i, ingredient in enumerate(recipe['ingredients'], 1):
                print(f"  {i}. {ingredient}")
        
            print("\nOptions:")
            print("1. Add ingredient")
            print("2. Remove ingredient")
            print("3. Edit ingredient")
            print("4. Clear all (start fresh)")
            print("5. Done editing ingredients")
        
            choice = input("\nEnter choice (1-5): ").strip()
        
            if choice == '1':
                # Add ingredient
                new_ingredient = input("Enter new ingredient: ").strip()
                if new_ingredient:
                    recipe['ingredients'].append(new_ingredient)
                    print(f"Added: {new_ingredient}")
        
            elif choice == '2':
                # Remove ingredient
                try:
                    num = int(input("Enter ingredient number to remove: ").strip())
                    if 1 <= num <= len(recipe['ingredients']):
                        removed = recipe['ingredients'].pop(num - 1)
                        print(f"Removed: {removed}")
                    else:
                        print("Invalid number")
                except ValueError:
                    print("Please enter a number")
        
            elif choice == '3':
                # Edit ingredient
                try:
                    num = int(input("Enter ingredient number to edit: ").strip())
                    if 1 <= num <= len(recipe['ingredients']):
                        current = recipe['ingredients'][num - 1]
                        print(f"\nCurrent: {current}")
                        new_text = input("Enter new text: ").strip()
                        if new_text:
                            recipe['ingredients'][num - 1] = new_text
                            print(f"Updated")
                    else:
                        print("Invalid number")
                except ValueError:
                    print("Please enter a number")
        
            elif choice == '4':
                # Clear all
                confirm = input("WARNING: Clear all ingredients? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    recipe['ingredients'] = []
                    print("All ingredients cleared")
        
            elif choice == '5':
                break
        
            else:
                print("Invalid choice")


    def edit_directions(self, recipe: Dict) -> None:
        """Edit recipe directions interactively.
    
        Args:
            recipe: Recipe dictionary to modify
        """
        print("\n" + "─"*40)
        print("EDIT DIRECTIONS")
        print("─"*40)
    
        directions = recipe['directions']
    
        # Handle both string and list formats
        if isinstance(directions, list):
            print("\nCurrent directions:")
            for i, step in enumerate(directions, 1):
                print(f"  {i}. {step}")
        
            print("\nEnter 'list' to edit as list, or 'text' to convert to paragraph:")
            mode = input("Mode: ").strip().lower()
        
            if mode == 'text':
                # Convert to paragraph
                text = ' '.join(directions)
                print(f"\nCurrent text:\n{text}\n")
                new_text = input("Enter new directions (or press Enter to keep): ").strip()
                if new_text:
                    recipe['directions'] = new_text
                    print("Directions updated")
            else:
                # Edit as list
                self.edit_directions_list(recipe)
        else:
            # String format
            print(f"\nCurrent directions:\n{directions}\n")

            print("Enter 'edit' to replace, or 'list' to split into steps:")
            mode = input("Mode: ").strip().lower()

            if mode == 'list':
                # Split into list
                print("\nEnter each step on a new line. Type 'done' when finished:")
                steps = []
                while True:
                    step = input(f"Step {len(steps) + 1}: ").strip()
                    if step.lower() == 'done':
                        break
                    if step:
                        steps.append(step)
            
                if steps:
                    recipe['directions'] = steps
                    print(f"Split into {len(steps)} steps")
            else:
                # Replace text
                new_text = input("Enter new directions: ").strip()
                if new_text:
                    recipe['directions'] = new_text
                    print("Directions updated")


    def edit_directions_list(self, recipe: Dict) -> None:
        """Edit directions when formatted as list.

        Args:
            recipe: Recipe dictionary to modify
        """
        while True:
            directions = recipe['directions']

            print(f"\nSteps ({len(directions)}):")
            for i, step in enumerate(directions, 1):
                preview = step[:60] + "..." if len(step) > 60 else step
                print(f"  {i}. {preview}")

            print("\nOptions:")
            print("1. Add step")
            print("2. Remove step")
            print("3. Edit step")
            print("4. Reorder steps")
            print("5. Done")

            choice = input("\nEnter choice (1-5): ").strip()

            if choice == '1':
                new_step = input("Enter new step: ").strip()
                if new_step:
                    directions.append(new_step)
                    print(f"Added step {len(directions)}")

            elif choice == '2':
                try:
                    num = int(input("Enter step number to remove: ").strip())
                    if 1 <= num <= len(directions):
                        removed = directions.pop(num - 1)
                        print(f"Removed step")
                    else:
                        print("Invalid number")
                except ValueError:
                    print("Please enter a number")

            elif choice == '3':
                try:
                    num = int(input("Enter step number to edit: ").strip())
                    if 1 <= num <= len(directions):
                        print(f"\nCurrent: {directions[num - 1]}")
                        new_text = input("Enter new text: ").strip()
                        if new_text:
                            directions[num - 1] = new_text
                            print(f"Updated")
                    else:
                        print("Invalid number")
                except ValueError:
                    print("Please enter a number")

            elif choice == '4':
                print("Enter new order as comma-separated numbers")
                print(f"Example: 1,3,2,4 to swap steps 2 and 3")
                order = input("New order: ").strip()

                try:
                    indices = [int(x.strip()) - 1 for x in order.split(',')]
                    if len(indices) == len(directions) and all(0 <= i < len(directions) for i in indices):
                        recipe['directions'] = [directions[i] for i in indices]
                        print("Steps reordered")
                    else:
                        print("Invalid order")
                except:
                    print("Invalid format")
        
            elif choice == '5':
                break
        
            else:
                print("Invalid choice")


    
    # ═══════════════════════════════════════════════════════════════
    # CREATE SHOPPING LIST
    # ═══════════════════════════════════════════════════════════════

    def create_shopping_list_workflow(self) -> None:
        """Handle shopping list creation with multi-day meal planning."""
        print("\n" + "="*60)
        print("CREATE SHOPPING LIST")
        print("="*60)
        
        # Get number of days
        while True:
            days_input = input("\nHow many days are you shopping for? (1-14): ").strip()
            try:
                num_days = int(days_input)
                if 1 <= num_days <= 14:
                    break
                else:
                    print("Please enter a number between 1 and 14.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Collect recipes for each day
        all_selected_recipes = []
        all_servings = {}
        
        for day in range(1, num_days + 1):
            print(f"\n{'─'*60}")
            print(f"DAY {day} of {num_days}")
            print("─"*60)
            
            day_recipes = self.select_recipes_for_day(day)
            
            if not day_recipes:
                print(f"(No recipes selected for Day {day})")
                continue
            
            # Get servings for each recipe
            for recipe_name in day_recipes:
                if recipe_name not in all_servings:
                    all_servings[recipe_name] = 0
                
                servings = self.get_servings_input(recipe_name)
                all_servings[recipe_name] += servings
                
                # Add to list if not already there
                if recipe_name not in [r['name'] for r in all_selected_recipes]:
                    recipe = self.recipe_book.get_recipe(recipe_name)
                    all_selected_recipes.append(recipe)
        
        if not all_selected_recipes:
            print("\nNo recipes selected. Shopping list not created.")
            return
        
        # Compile shopping list
        print(f"\nCompiling shopping list from {len(all_selected_recipes)} recipes...")
        
        try:
            shopping_list = compile_shopping_list(all_selected_recipes, all_servings)
            self.current_shopping_list = shopping_list
            
            # Add to history
            self.add_to_history(all_selected_recipes, all_servings, shopping_list)
            
            # Display summary
            self.display_shopping_list_summary(shopping_list, all_selected_recipes)
            
            print(f"\nShopping list created successfully!")
            
            # Offer to export
            export_now = input("\nExport this list now? (y/n): ").strip().lower()
            if export_now == 'y':
                self.export_current_list()
        
        except Exception as e:
            print(f"Error creating shopping list: {e}")
    
    def select_recipes_for_day(self, day: int) -> List[str]:
        """Select recipes for a specific day.
        
        Args:
            day: Day number
            
        Returns:
            List of selected recipe names
        """
        selected = []
        
        while True:
            # Show options
            print(f"\nDay {day} - Select recipes:")
            print("1. Browse all recipes")
            print("2. Filter by tag")
            print("3. Search by keyword")
            print("4. Done selecting for this day")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '4':
                break
            
            # Get available recipes based on choice
            available_recipes = []
            
            if choice == '1':
                available_recipes = self.recipe_book.list_recipe_names()
            
            elif choice == '2':
                all_tags = self.recipe_book.get_all_tags()
                if not all_tags:
                    print("No tags available.")
                    continue
                
                print("\nAvailable tags:")
                tags_list = sorted(all_tags)
                for i, tag in enumerate(tags_list, 1):
                    print(f"{i}. {tag}")
                
                tag_input = input("\nEnter tag name or number: ").strip()
                
                if tag_input.isdigit():
                    idx = int(tag_input) - 1
                    if 0 <= idx < len(tags_list):
                        tag = tags_list[idx]
                        recipes_with_tag = self.recipe_book.search_by_tag(tag)
                        available_recipes = [r['name'] for r in recipes_with_tag]
                else:
                    recipes_with_tag = self.recipe_book.search_by_tag(tag_input)
                    available_recipes = [r['name'] for r in recipes_with_tag]
            
            elif choice == '3':
                keyword = input("\nEnter search keyword: ").strip()
                if keyword:
                    results = self.recipe_book.search_recipes(keyword)
                    available_recipes = [r['name'] for r in results]
            
            else:
                print("Invalid choice.")
                continue
            
            if not available_recipes:
                print("No recipes found.")
                continue
            
            # Display and select
            print(f"\nAvailable recipes ({len(available_recipes)}):")
            for i, name in enumerate(available_recipes, 1):
                selected_mark = "✓" if name in selected else " "
                print(f"[{selected_mark}] {i}. {name}")

            # ----- added during bug fixes: multi-select recipes for a day w/ comma separation -----
            print("\n Tip: Enter multiple numbers separated by commas (e.g., '1, 3, 5')")
            selection = input("Enter recipe number(s) or 'done': ").strip()
            if selection.lower() == 'done':
                continue

            # split by comma and process each selection
            selections = [s.strip() for s in selection.split(',')]

            for sel in selections:
                try:
                    idx = int(sel) - 1
                    if 0 <= idx < len(available_recipes):
                        recipe_name = available_recipes[idx]
                        if recipe_name not in selected:
                            selected.append(recipe_name)
                            print(f"     Added: {recipe_name}")
                        else:
                            print(f"     (Already selected: {recipe_name})")
                    else:
                        print(f"     Invalid recipe number: {sel}")
                except ValueError:
                    print(f"     Invalid input: {sel} (must be a number)")
            # --------------------------------------------------------------------------------------
        return selected
    
    def get_servings_input(self, recipe_name: str) -> int:
        """Get servings input for a recipe.
        
        Args:
            recipe_name: Name of recipe
            
        Returns:
            Number of servings
        """
        default = self.settings.get('default_servings', 4)
        
        while True:
            servings_input = input(
                f"  Servings for '{recipe_name}' [default: {default}]: "
            ).strip()
            
            if not servings_input:
                return default
            
            try:
                servings = int(servings_input)
                if servings > 0:
                    return servings
                else:
                    print("     Please enter a positive number.")
            except ValueError:
                print("     Please enter a valid number.")
    
    def display_shopping_list_summary(self, shopping_list: Dict, recipes: List[Dict]) -> None:
        """Display summary of shopping list.
        
        Args:
            shopping_list: Compiled shopping list
            recipes: List of recipes used
        """
        # Group by category
        categorized = group_items_by_category(shopping_list)
        
        print("\n" + "="*60)
        print("SHOPPING LIST SUMMARY")
        print("="*60)
        
        print(f"\nRecipes included: {', '.join([r['name'] for r in recipes])}")
        
        total_items = sum(len(items) for items in categorized.values())
        print(f"Total items: {total_items}")
        
        print("\nItems by category:")
        for category, items in categorized.items():
            print(f"\n  {category.upper().replace('_', ' ')} ({len(items)} items)")
            for item_name, item_data in list(items.items())[:3]:  # Show first 3
                qty = item_data['quantity']
                unit = item_data['unit']
                print(f"    • {item_name}: {qty} {unit}")
            if len(items) > 3:
                print(f"    ... and {len(items) - 3} more")
    
    def add_to_history(self, recipes: List[Dict], servings: Dict, shopping_list: Dict) -> None:
        """Add shopping list to history (last 5).
        
        Args:
            recipes: List of recipes
            servings: Servings dictionary
            shopping_list: Compiled shopping list
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'recipe_names': [r['name'] for r in recipes],
            'servings': servings,
            'total_items': len(shopping_list),
            'shopping_list': shopping_list
        }
        
        # Add to beginning of list
        self.shopping_history.insert(0, entry)
        
        # Keep only last 5
        self.shopping_history = self.shopping_history[:5]
    
    # ═══════════════════════════════════════════════════════════════
    # COMPARE STORE PRICES
    # ═══════════════════════════════════════════════════════════════
    
    def compare_prices_workflow(self) -> None:
        """Handle store price comparison."""
        print("\n" + "="*60)
        print("COMPARE STORE PRICES")
        print("="*60)
        
        # Check if there's a current shopping list
        if not self.current_shopping_list:
            print("\nNo shopping list available.")
            print("  Create a shopping list first (Option 3).")
            return
        
        # Get stores to compare
        preferred_stores = self.settings.get('preferred_stores', ['safeway', 'giant', 'trader_joes'])
        
        print(f"\nPreferred stores: {', '.join(preferred_stores)}")
        use_preferred = input("Use these stores? (y/n): ").strip().lower()
        
        if use_preferred != 'y':
            print("\nAvailable stores: safeway, giant, trader_joes")
            stores_input = input("Enter store names (comma-separated): ").strip()
            if stores_input:
                stores = [s.strip() for s in stores_input.split(',')]
            else:
                stores = preferred_stores
        else:
            stores = preferred_stores
        
        # Compare prices
        print(f"\nComparing prices across {len(stores)} stores...")
        
        try:
            comparison = compare_store_totals(self.current_shopping_list, stores)
            
            # Display results
            print("\n" + "="*60)
            print("PRICE COMPARISON RESULTS")
            print("="*60)
            
            for i, (store_name, info) in enumerate(comparison.items(), 1):
                print(f"\n{i}. {store_name.upper()}")
                print(f"   Total: ${info['total']:.2f}")
                print(f"   Items found: {info['items_found']}")
                print(f"   Items missing: {info['items_missing']}")
            
            # Show best option
            cheapest = list(comparison.keys())[0]
            print(f"\nBest value: {cheapest.upper()} (${comparison[cheapest]['total']:.2f})")
            
        except Exception as e:
            print(f"Error comparing prices: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # EXPORT SHOPPING LIST
    # ═══════════════════════════════════════════════════════════════
    
    def export_shopping_list_workflow(self) -> None:
        """Handle shopping list export from history."""
        print("\n" + "="*60)
        print("EXPORT SHOPPING LIST")
        print("="*60)
        
        if not self.shopping_history:
            print("\nNo shopping lists in history.")
            print("  Create a shopping list first (Option 3).")
            return
        
        # Show last 5 lists
        print(f"\nRecent shopping lists ({len(self.shopping_history)}):")
        print("─"*60)
        
        for i, entry in enumerate(self.shopping_history, 1):
            timestamp = datetime.fromisoformat(entry['timestamp'])
            date_str = timestamp.strftime("%Y-%m-%d %H:%M")
            recipes = ', '.join(entry['recipe_names'])
            print(f"{i}. [{date_str}] {recipes}")
            print(f"   ({entry['total_items']} items)")
        
        # Select list
        selection = input(f"\nSelect list to export (1-{len(self.shopping_history)}): ").strip()
        
        try:
            idx = int(selection) - 1
            if 0 <= idx < len(self.shopping_history):
                selected_list = self.shopping_history[idx]['shopping_list']
                selected_recipes = self.shopping_history[idx]['recipe_names']
                self.export_shopping_list(selected_list, selected_recipes)
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a valid number.")
    
    def export_current_list(self) -> None:
        """Export the current shopping list."""
        if not self.current_shopping_list:
            print("No current shopping list.")
            return
        
        recipe_names = self.shopping_history[0]['recipe_names'] if self.shopping_history else []
        self.export_shopping_list(self.current_shopping_list, recipe_names)
    
    def export_shopping_list(self, shopping_list: Dict, recipe_names: List[str]) -> None:
        """Export a shopping list to file.
        
        Args:
            shopping_list: Shopping list to export
            recipe_names: Names of recipes in list
        """
        # Get format
        default_format = self.settings.get('default_export_format', 'pdf')
        print(f"\nExport format options: csv, pdf, txt [default: {default_format}]")
        format_input = input("Enter format: ").strip().lower()
        
        if not format_input:
            format_input = default_format
        
        if format_input not in ['csv', 'pdf', 'txt']:
            print("✗ Invalid format. Using default.")
            format_input = default_format
        
        # Get filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"shopping_list_{timestamp}.{format_input}"
        
        filename_input = input(f"Filename [{default_filename}]: ").strip()
        if not filename_input:
            filename_input = default_filename
        
        # Ensure correct extension
        if not filename_input.endswith(f".{format_input}"):
            filename_input += f".{format_input}"
        
        # Create exports directory
        export_dir = self.settings.get('export_directory', 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        filepath = os.path.join(export_dir, filename_input)
        
        # Export options
        print("\nExport options:")
        categorize = input("  Categorize items? (y/n) [y]: ").strip().lower() != 'n'
        
        title_input = input("  Custom title [Shopping List]: ").strip()
        title = title_input if title_input else "Shopping List"
        
        # this was giving us buggy pdf title formatting but I'm not deleting the code (yet)
        #if recipe_names:
            #title += f"\nRecipes: {', '.join(recipe_names)}"
        
        # Perform export
        try:
            print(f"\nExporting to {filepath}...")
            
            if format_input == 'csv':
                export_to_csv(shopping_list, filepath, categorize=categorize)
            elif format_input == 'pdf':
                export_to_pdf(shopping_list, filepath, title=title, categorize=categorize, recipe_names=recipe_names)
                # adds recipe metadata after export
                if recipe_names:
                    print(f"   Recipes: {', '.join(recipe_names)}")
            elif format_input == 'txt':
                export_to_txt(shopping_list, filepath, title=title, categorize=categorize)
            
            print(f"Shopping list exported successfully!")
            print(f"  Location: {filepath}")
            
        except Exception as e:
            print(f"Error exporting: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # SETTINGS
    # ═══════════════════════════════════════════════════════════════
    
    def settings_workflow(self) -> None:
        """Handle settings management."""
        while True:
            print("\n" + "="*60)
            print("SETTINGS")
            print("="*60)
            
            print(f"\n1. Default Servings: {self.settings.get('default_servings', 4)}")
            print(f"2. Preferred Stores: {', '.join(self.settings.get('preferred_stores', []))}")
            print(f"3. Default Export Format: {self.settings.get('default_export_format', 'pdf')}")
            print(f"4. Export Directory: {self.settings.get('export_directory', 'exports')}")
            print("5. Save & Return")
            
            choice = input("\nEnter setting to change (1-5): ").strip()
            
            if choice == '1':
                self.change_default_servings()
            elif choice == '2':
                self.change_preferred_stores()
            elif choice == '3':
                self.change_export_format()
            elif choice == '4':
                self.change_export_directory()
            elif choice == '5':
                self.save_settings()
                break
            else:
                print("Invalid choice.")
    
    def change_default_servings(self) -> None:
        """Change default servings setting."""
        current = self.settings.get('default_servings', 4)
        new_value = input(f"Enter new default servings [{current}]: ").strip()
        
        if new_value:
            try:
                servings = int(new_value)
                if servings > 0:
                    self.settings['default_servings'] = servings
                    print(f"Default servings set to {servings}")
                else:
                    print("Must be a positive number.")
            except ValueError:
                print("Invalid number.")
    
    def change_preferred_stores(self) -> None:
        """Change preferred stores setting."""
        current = self.settings.get('preferred_stores', [])
        print(f"\nCurrent: {', '.join(current)}")
        print("Available: safeway, giant, trader_joes")
        
        new_stores = input("Enter store names (comma-separated): ").strip()
        
        if new_stores:
            stores = [s.strip() for s in new_stores.split(',')]
            self.settings['preferred_stores'] = stores
            print(f"Preferred stores updated")
    
    def change_export_format(self) -> None:
        """Change default export format setting."""
        current = self.settings.get('default_export_format', 'pdf')
        print(f"\nCurrent: {current}")
        print("Options: csv, pdf, txt")
        
        new_format = input("Enter new default format: ").strip().lower()
        
        if new_format in ['csv', 'pdf', 'txt']:
            self.settings['default_export_format'] = new_format
            print(f"Default export format set to {new_format}")
        else:
            print("Invalid format.")
    
    def change_export_directory(self) -> None:
        """Change export directory setting."""
        current = self.settings.get('export_directory', 'exports')
        new_dir = input(f"Enter new export directory [{current}]: ").strip()
        
        if new_dir:
            self.settings['export_directory'] = new_dir
            print(f"✓ Export directory set to {new_dir}")
    
    # ═══════════════════════════════════════════════════════════════
    # EXIT
    # ═══════════════════════════════════════════════════════════════
    
    def exit_application(self) -> None:
        """Handle application exit."""
        print("\n" + "="*60)
        print("Thanks for using Cornucopia Grocery Assistant!")
        print("="*60)
        print("\n Happy shopping! \n")


def main():
    """Main entry point."""
    app = CornucopiaApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted. Goodbye!")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()