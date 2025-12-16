"""
Integration Tests for Cornucopia Grocery List System
INST326 Project 4 - DDM Team

Tests interactions between major components.
Run with: python -m unittest tests.test_integration -v
"""

import unittest, tempfile, shutil
import os, sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.RecipeBook import RecipeBook
from src.recipe_parser import TXTRecipeParser, PDFRecipeParser
from src.shopping_list import compile_shopping_list
from src.store_data import load_store_data, calculate_shopping_list_total, compare_store_totals
from src.export_utils import export_to_csv, export_to_pdf, export_to_txt


class TestRecipeToRecipeBook(unittest.TestCase):
    """Test recipe parsing and RecipeBook storage integration"""
    
    def setUp(self):
        """Create temporary recipe book"""
        self.temp_dir = tempfile.mkdtemp()
        self.recipe_book = RecipeBook(os.path.join(self.temp_dir, "recipe_book.json"))
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)
    
    def test_parse_and_save_txt_recipe(self):
        """Test parsing TXT recipe and saving to RecipeBook"""
        recipe_path = 'data/sample_recipes/scrambled_eggs.txt'
        
        if os.path.exists(recipe_path):
            parser = TXTRecipeParser(recipe_path)
            self.assertTrue(parser.validate_format())
            
            recipe = parser.parse()
            self.assertIn('name', recipe)
            self.assertIn('ingredients', recipe)
            
            # Save to recipe book
            self.recipe_book.add_recipe(recipe)
            
            # Verify saved
            self.assertEqual(self.recipe_book.count_recipes(), 1)
            retrieved = self.recipe_book.get_recipe(recipe['name'])
            self.assertIsNotNone(retrieved)
    
    def test_persistence_across_sessions(self):
        """Test that recipes persist when RecipeBook is reloaded"""
        recipe_path = 'data/sample_recipes/avocado_toast.txt'
        
        if os.path.exists(recipe_path):
            # Session 1
            parser = TXTRecipeParser(recipe_path)
            recipe = parser.parse()
            self.recipe_book.add_recipe(recipe)
            recipe_name = recipe['name']
            
            # Close and reopen (simulate new session)
            book_path = self.recipe_book.filepath
            del self.recipe_book
            
            # Session 2
            new_book = RecipeBook(str(book_path))
            retrieved = new_book.get_recipe(recipe_name)
            
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved['name'], recipe_name)


class TestRecipeBookToShoppingList(unittest.TestCase):
    """Test creating shopping lists from RecipeBook"""
    
    def setUp(self):
        """Create recipe book with test recipes"""
        self.temp_dir = tempfile.mkdtemp()
        self.recipe_book = RecipeBook(os.path.join(self.temp_dir, "recipe_book.json"))
        
        # Add test recipes
        self.recipes = [
            {
                'name': 'Simple Pasta',
                'ingredients': ['1 lb pasta', '2 cups tomato sauce'],
                'directions': 'Cook pasta',
                'tags': ['dinner']
            },
            {
                'name': 'Basic Salad',
                'ingredients': ['2 cups lettuce', '1 tomato'],
                'directions': 'Toss salad',
                'tags': ['lunch']
            }
        ]
        
        for recipe in self.recipes:
            self.recipe_book.add_recipe(recipe)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)
    
    def test_compile_shopping_list_from_recipes(self):
        """Test compiling shopping list from multiple recipes"""
        # Get recipes from book
        recipe1 = self.recipe_book.get_recipe('Simple Pasta')
        recipe2 = self.recipe_book.get_recipe('Basic Salad')
        
        recipes = [recipe1, recipe2]
        servings = {r['name']: 2 for r in recipes}
        
        # Compile shopping list
        shopping_list = compile_shopping_list(recipes, servings)
        
        # Verify list created
        self.assertGreater(len(shopping_list), 0)
        self.assertIn('pasta', shopping_list)
    
    def test_tag_filtering_to_shopping_list(self):
        """Test filtering recipes by tag and creating shopping list"""
        # Filter by dinner tag
        dinner_recipes = self.recipe_book.search_by_tag('dinner')
        
        self.assertEqual(len(dinner_recipes), 1)
        self.assertEqual(dinner_recipes[0]['name'], 'Simple Pasta')
        
        # Create shopping list from filtered recipes
        servings = {r['name']: 1 for r in dinner_recipes}
        shopping_list = compile_shopping_list(dinner_recipes, servings)
        
        self.assertIn('pasta', shopping_list)
        self.assertNotIn('lettuce', shopping_list)  # Not in dinner recipe


class TestShoppingListToStoreComparison(unittest.TestCase):
    """Test shopping list price comparison across stores"""
    
    def test_calculate_total_at_store(self):
        """Test calculating shopping list total at single store"""
        shopping_list = {
            'milk': {'quantity': 1, 'unit': 'gallon', 'recipes': ['Cereal']},
            'egg': {'quantity': 6, 'unit': 'count', 'recipes': ['Breakfast']}
        }
        
        # Load store data
        inventory = load_store_data('safeway')
        
        # Calculate total
        result = calculate_shopping_list_total(shopping_list, inventory)
        
        self.assertIn('total', result)
        self.assertIn('itemized', result)
        self.assertIn('not_found', result)
        self.assertIsInstance(result['total'], float)
    
    def test_compare_multiple_stores(self):
        """Test comparing prices across multiple stores"""
        shopping_list = {
            'milk': {'quantity': 1, 'unit': 'gallon', 'recipes': ['Cereal']},
            'cheese': {'quantity': 1, 'unit': 'lb', 'recipes': ['Sandwich']}
        }
        
        stores = ['safeway', 'giant']
        comparison = compare_store_totals(shopping_list, stores)
        
        # Verify comparison structure
        self.assertEqual(len(comparison), 2)
        self.assertIn('safeway', comparison)
        self.assertIn('giant', comparison)
        
        # Verify sorted by price (cheapest first)
        prices = [data['total'] for data in comparison.values()]
        self.assertEqual(prices, sorted(prices))


class TestShoppingListToExport(unittest.TestCase):
    """Test exporting shopping lists to different formats"""
    
    def setUp(self):
        """Create temporary directory for exports"""
        self.temp_dir = tempfile.mkdtemp()
        
        self.shopping_list = {
            'milk': {'quantity': 1, 'unit': 'gallon', 'recipes': ['Cereal'], 'price': 3.99},
            'egg': {'quantity': 12, 'unit': 'count', 'recipes': ['Breakfast'], 'price': 4.50}
        }
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)
    
    def test_export_to_csv(self):
        """Test CSV export"""
        filepath = os.path.join(self.temp_dir, "test.csv")
        result = export_to_csv(self.shopping_list, filepath)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filepath))
        self.assertGreater(os.path.getsize(filepath), 0)
    
    def test_export_to_pdf(self):
        """Test PDF export"""
        filepath = os.path.join(self.temp_dir, "test.pdf")
        result = export_to_pdf(self.shopping_list, filepath)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filepath))
        
        # Verify it's a PDF
        with open(filepath, 'rb') as f:
            header = f.read(5)
            self.assertEqual(header, b'%PDF-')
    
    def test_export_to_txt(self):
        """Test TXT export"""
        filepath = os.path.join(self.temp_dir, "test.txt")
        result = export_to_txt(self.shopping_list, filepath)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filepath))
        
        # Verify content
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('milk', content.lower())
            self.assertIn('egg', content.lower())
    
    def test_export_all_formats(self):
        """Test exporting same list to all formats"""
        formats = [
            ('test.csv', export_to_csv),
            ('test.pdf', export_to_pdf),
            ('test.txt', export_to_txt)
        ]
        
        for filename, export_func in formats:
            filepath = os.path.join(self.temp_dir, filename)
            result = export_func(self.shopping_list, filepath)
            self.assertTrue(result, f"Failed to export {filename}")
            self.assertTrue(os.path.exists(filepath), f"{filename} not created")


class TestCompleteUserJourney(unittest.TestCase):
    """Test complete workflow from import to export"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.recipe_book = RecipeBook(os.path.join(self.temp_dir, "recipe_book.json"))
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_workflow(self):
        """Test: Import --> Save --> Create List --> Compare --> Export"""
        
        # Step 1: Import recipe
        recipe_path = 'data/sample_recipes/scrambled_eggs.txt'
        if not os.path.exists(recipe_path):
            self.skipTest("Sample recipe file not found")
        
        parser = TXTRecipeParser(recipe_path)
        recipe = parser.parse()
        
        # Step 2: Save to RecipeBook
        self.recipe_book.add_recipe(recipe)
        self.assertEqual(self.recipe_book.count_recipes(), 1)
        
        # Step 3: Create shopping list
        recipes = [recipe]
        servings = {recipe['name']: 2}
        shopping_list = compile_shopping_list(recipes, servings)
        self.assertGreater(len(shopping_list), 0)
        
        # Step 4: Compare stores
        comparison = compare_store_totals(shopping_list, ['safeway', 'giant'])
        self.assertEqual(len(comparison), 2)
        
        # Step 5: Export
        export_path = os.path.join(self.temp_dir, "final_list.pdf")
        result = export_to_pdf(shopping_list, export_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(export_path))


class TestErrorRecovery(unittest.TestCase):
    """Test error handling and recovery"""
    
    def test_invalid_recipe_handling(self):
        """Test system handles invalid recipe gracefully"""
        temp_dir = tempfile.mkdtemp()
        try:
            recipe_book = RecipeBook(os.path.join(temp_dir, "recipe_book.json"))
            
            # Try to add invalid recipe
            with self.assertRaises((TypeError, KeyError)):
                recipe_book.add_recipe("not a dict")
            
            # System should still work
            valid_recipe = {
                'name': 'Valid Recipe',
                'ingredients': ['ingredient'],
                'directions': 'directions'
            }
            recipe_book.add_recipe(valid_recipe)
            self.assertEqual(recipe_book.count_recipes(), 1)
        
        finally:
            shutil.rmtree(temp_dir)
    
    def test_missing_store_data_handling(self):
        """Test handling of missing store data"""
        shopping_list = {
            'item': {'quantity': 1, 'unit': 'each', 'recipes': ['Recipe']}
        }
        
        # Try to compare with non-existent store
        comparison = compare_store_totals(shopping_list, ['nonexistent_store'])
        
        # Should not crash, should return something
        self.assertIsInstance(comparison, dict)


if __name__ == '__main__':
    unittest.main(verbosity=2)