"""
System Tests for Cornucopia Grocery List System
INST326 Project 4 - DDM Team

Tests complete user workflows from end to end.
Run with: python -m unittest tests.test_system -v
"""

import unittest, tempfile, shutil
import os, sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.RecipeBook import RecipeBook
from src.recipe_parser import TXTRecipeParser, PDFRecipeParser, DOCXRecipeParser
from src.shopping_list import compile_shopping_list
from src.store_data import load_store_data, calculate_shopping_list_total, compare_store_totals
from src.export_utils import export_to_csv, export_to_pdf, export_to_txt


class TestCompleteRecipeWorkflow(unittest.TestCase):
    """Test complete workflow: import → save → create list → compare → export"""
    
    def setUp(self):
        """Create temporary directories for test"""
        self.temp_dir = tempfile.mkdtemp()
        self.recipe_book = RecipeBook(os.path.join(self.temp_dir, "recipe_book.json"))
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_user_journey(self):
        """Test full user journey from recipe import to shopping list export"""
        
        # Import 3 recipes (TXT, PDF, DOCX)
        recipe_files = [
            ('data/sample_recipes/scrambled_eggs.txt', TXTRecipeParser),
            ('data/sample_recipes/veggie_quesadilla.pdf', PDFRecipeParser),
            ('data/sample_recipes/greek_yogurt_parfait.docx', DOCXRecipeParser)
        ]
        
        recipes_imported = []
        for filepath, parser_class in recipe_files:
            if os.path.exists(filepath):
                parser = parser_class(filepath)
                if parser.validate_format():
                    recipe = parser.parse()
                    recipe['tags'] = ['breakfast']  # Add tag
                    self.recipe_book.add_recipe(recipe)
                    recipes_imported.append(recipe['name'])
        
        # Verify recipes were added
        self.assertGreaterEqual(len(recipes_imported), 2)  # At least 2 should work
        
        # Create shopping list from recipes
        recipes = [self.recipe_book.get_recipe(name) for name in recipes_imported]
        servings = {r['name']: 2 for r in recipes}
        shopping_list = compile_shopping_list(recipes, servings)
        
        # Verify shopping list created
        self.assertGreater(len(shopping_list), 5)  # Should have multiple items
        
        # Step 3: Compare prices across stores
        stores = ['safeway', 'giant']
        comparison = compare_store_totals(shopping_list, stores)
        
        # Verify comparison worked
        self.assertEqual(len(comparison), 2)
        self.assertIn('safeway', comparison)
        self.assertIn('giant', comparison)
        
        # Step 4: Export to PDF
        export_path = os.path.join(self.temp_dir, "test_list.pdf")
        result = export_to_pdf(shopping_list, export_path, title="Test Shopping List")
        
        # Verify export worked
        self.assertTrue(result)
        self.assertTrue(os.path.exists(export_path))
        self.assertGreater(os.path.getsize(export_path), 0)


class TestMultiDayMealPlanning(unittest.TestCase):
    """Test planning meals for multiple days and aggregating shopping list"""
    
    def setUp(self):
        """Create temporary recipe book"""
        self.temp_dir = tempfile.mkdtemp()
        self.recipe_book = RecipeBook(os.path.join(self.temp_dir, "recipe_book.json"))
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)
    
    def test_three_day_meal_plan(self):
        """Test creating shopping list for 3 days of meals"""
        
        # Import multiple recipes
        recipe_files = [
            'data/sample_recipes/scrambled_eggs.txt',
            'data/sample_recipes/avocado_toast.txt',
            'data/sample_recipes/veggie_quesadilla.pdf'
        ]
        
        recipes = []
        for filepath in recipe_files:
            if os.path.exists(filepath):
                if filepath.endswith('.txt'):
                    parser = TXTRecipeParser(filepath)
                elif filepath.endswith('.pdf'):
                    parser = PDFRecipeParser(filepath)
                
                if parser.validate_format():
                    recipe = parser.parse()
                    self.recipe_book.add_recipe(recipe)
                    recipes.append(recipe)
        
        # Plan 3 days: eggs (day 1 & 2), toast (day 2 & 3), quesadilla (day 1 & 3)
        # Simulates user selecting recipes for each day
        servings_dict = {}
        if len(recipes) >= 3:
            servings_dict[recipes[0]['name']] = 2  # eggs for 2 days
            servings_dict[recipes[1]['name']] = 2  # toast for 2 days
            servings_dict[recipes[2]['name']] = 2  # quesadilla for 2 days
        
        # Put together aggregated shopping list
        shopping_list = compile_shopping_list(recipes[:3], servings_dict)
        
        # Verify aggregation worked
        self.assertGreater(len(shopping_list), 3)
        
        # Verify quantities were scaled
        # (eggs appear in multiple recipes, should be aggregated)
        if 'egg' in shopping_list:
            self.assertGreater(shopping_list['egg']['quantity'], 2)


class TestPersistenceAcrossSessions(unittest.TestCase):
    """Test that data persists across program sessions"""
    
    def setUp(self):
        """Create temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.recipe_book_path = os.path.join(self.temp_dir, "recipe_book.json")
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)
    
    def test_recipe_persistence(self):
        """Test recipes persist after closing and reopening program"""
        
        # Session 1: Add recipes
        book1 = RecipeBook(self.recipe_book_path)
        
        test_recipe = {
            'name': 'Test Persistence Recipe',
            'ingredients': ['2 cups flour', '1 egg'],
            'directions': 'Mix and bake.',
            'tags': ['test']
        }
        book1.add_recipe(test_recipe)
        
        initial_count = book1.count_recipes()
        self.assertEqual(initial_count, 1)
        
        # Simulate closing program (delete book1 object)
        del book1
        
        # Session 2: Reopen and verify
        book2 = RecipeBook(self.recipe_book_path)
        
        # Verify recipe still exists
        self.assertEqual(book2.count_recipes(), initial_count)
        self.assertIn('Test Persistence Recipe', book2)
        
        retrieved = book2.get_recipe('Test Persistence Recipe')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['name'], 'Test Persistence Recipe')
        self.assertIn('test', retrieved['tags'])


class TestTagBasedOrganization(unittest.TestCase):
    """Test organizing and filtering recipes by tags"""
    
    def setUp(self):
        """Create recipe book with tagged recipes"""
        self.temp_dir = tempfile.mkdtemp()
        self.recipe_book = RecipeBook(os.path.join(self.temp_dir, "recipe_book.json"))
        
        # Add recipes with different tags
        recipes = [
            {
                'name': 'Breakfast Eggs',
                'ingredients': ['4 eggs'],
                'directions': 'Cook eggs',
                'tags': ['breakfast', 'quick', 'protein']
            },
            {
                'name': 'Dinner Pasta',
                'ingredients': ['1 lb pasta'],
                'directions': 'Cook pasta',
                'tags': ['dinner', 'italian']
            },
            {
                'name': 'Quick Salad',
                'ingredients': ['lettuce'],
                'directions': 'Toss salad',
                'tags': ['lunch', 'quick', 'healthy']
            }
        ]
        
        for recipe in recipes:
            self.recipe_book.add_recipe(recipe)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)
    
    def test_filter_and_create_shopping_list_by_tag(self):
        """Test creating shopping list from recipes filtered by tag"""
        
        # Filter for 'quick' recipes
        quick_recipes = self.recipe_book.search_by_tag('quick')
        
        # Verify filtering worked
        self.assertEqual(len(quick_recipes), 2)  # Eggs and Salad
        
        # Create shopping list from filtered recipes
        servings = {r['name']: 1 for r in quick_recipes}
        shopping_list = compile_shopping_list(quick_recipes, servings)
        
        # Verify shopping list contains items from quick recipes only
        self.assertGreater(len(shopping_list), 0)
        
        # Verify pasta is NOT in the list (not tagged 'quick')
        self.assertNotIn('pasta', shopping_list)


class TestStoreComparisonDecision(unittest.TestCase):
    """Test comparing stores and making shopping decision"""
    
    def test_find_cheapest_store(self):
        """Test identifying cheapest store for shopping list"""
        
        # Create sample shopping list
        shopping_list = {
            'milk': {'quantity': 1, 'unit': 'gallon', 'recipes': ['Cereal']},
            'egg': {'quantity': 12, 'unit': 'count', 'recipes': ['Breakfast']},
            'cheese': {'quantity': 1, 'unit': 'lb', 'recipes': ['Sandwich']}
        }
        
        # Compare stores
        stores = ['safeway', 'giant']
        comparison = compare_store_totals(shopping_list, stores)
        
        # Verify comparison worked
        self.assertEqual(len(comparison), 2)
        
        # Get cheapest store (first in sorted dict)
        cheapest_store = list(comparison.keys())[0]
        cheapest_total = comparison[cheapest_store]['total']
        
        # Verify it's actually cheapest
        for store_name, data in comparison.items():
            self.assertLessEqual(cheapest_total, data['total'])
        
        # Create recommendation message
        recommendation = f"Shop at {cheapest_store.upper()} for best value: ${cheapest_total:.2f}"
        
        self.assertIn(cheapest_store, recommendation.lower())
        self.assertIn(str(cheapest_total), recommendation)


if __name__ == '__main__':
    unittest.main(verbosity=2)