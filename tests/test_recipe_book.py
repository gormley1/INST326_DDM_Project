"""
Unit tests for RecipeBook class.

Tests cover:
- Adding recipes
- Retrieving recipes
- Removing recipes
- Updating recipes
- Searching recipes
- Data persistence (save/load)
- Import/export functionality
- Error handling

Author: DDM Team - Matthew Gormley
Course: INST326
Date: December 2024
"""

import unittest
import json
import tempfile
from pathlib import Path
import sys
import os

# Add parent directory to path to import RecipeBook
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.RecipeBook import RecipeBook


class TestRecipeBookBasics(unittest.TestCase):
    """Test basic RecipeBook functionality."""
    
    def setUp(self):
        """Create temporary recipe book for testing."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.close()
        self.book = RecipeBook(self.temp_file.name)
        
        # Sample recipe for testing
        self.sample_recipe = {
            'name': 'Test Recipe',
            'ingredients': ['1 cup flour', '2 eggs', '1 cup milk'],
            'directions': 'Mix ingredients. Bake at 350°F for 30 minutes.'
        }
    
    def tearDown(self):
        """Clean up temporary file."""
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_create_empty_recipe_book(self):
        """Test creating a new empty recipe book."""
        self.assertEqual(len(self.book), 0)
        self.assertEqual(self.book.count_recipes(), 0)
    
    def test_add_recipe(self):
        """Test adding a recipe."""
        self.book.add_recipe(self.sample_recipe)
        self.assertEqual(self.book.count_recipes(), 1)
        self.assertIn('Test Recipe', self.book)
    
    def test_add_duplicate_recipe_raises_error(self):
        """Test that adding duplicate recipe raises ValueError."""
        self.book.add_recipe(self.sample_recipe)
        
        with self.assertRaises(ValueError) as context:
            self.book.add_recipe(self.sample_recipe)
        
        self.assertIn("already exists", str(context.exception))
    
    def test_add_invalid_recipe_raises_error(self):
        """Test that adding invalid recipe raises appropriate errors."""
        # Not a dictionary
        with self.assertRaises(TypeError):
            self.book.add_recipe("not a dict")
        
        # Missing required fields
        invalid_recipe = {'name': 'Incomplete'}
        with self.assertRaises(KeyError):
            self.book.add_recipe(invalid_recipe)
    
    def test_get_recipe(self):
        """Test retrieving a recipe."""
        self.book.add_recipe(self.sample_recipe)
        
        retrieved = self.book.get_recipe('Test Recipe')
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['name'], 'Test Recipe')
        self.assertEqual(len(retrieved['ingredients']), 3)
    
    def test_get_recipe_case_insensitive(self):
        """Test that recipe retrieval is case-insensitive."""
        self.book.add_recipe(self.sample_recipe)
        
        # Try different cases
        self.assertIsNotNone(self.book.get_recipe('test recipe'))
        self.assertIsNotNone(self.book.get_recipe('TEST RECIPE'))
        self.assertIsNotNone(self.book.get_recipe('TeSt ReCiPe'))
    
    def test_get_nonexistent_recipe(self):
        """Test that getting nonexistent recipe returns None."""
        result = self.book.get_recipe('Nonexistent Recipe')
        self.assertIsNone(result)
    
    def test_list_recipes(self):
        """Test listing all recipes."""
        recipes = [
            {
                'name': 'Recipe 1',
                'ingredients': ['ingredient 1'],
                'directions': 'directions 1'
            },
            {
                'name': 'Recipe 2',
                'ingredients': ['ingredient 2'],
                'directions': 'directions 2'
            },
            {
                'name': 'Recipe 3',
                'ingredients': ['ingredient 3'],
                'directions': 'directions 3'
            }
        ]
        
        for recipe in recipes:
            self.book.add_recipe(recipe)
        
        all_recipes = self.book.list_recipes()
        
        self.assertEqual(len(all_recipes), 3)
        self.assertEqual(all_recipes[0]['name'], 'Recipe 1')
    
    def test_list_recipe_names(self):
        """Test getting list of recipe names."""
        recipes = [
            {'name': 'Pasta', 'ingredients': ['pasta'], 'directions': 'cook'},
            {'name': 'Salad', 'ingredients': ['lettuce'], 'directions': 'toss'},
            {'name': 'Bread', 'ingredients': ['flour'], 'directions': 'bake'}
        ]
        
        for recipe in recipes:
            self.book.add_recipe(recipe)
        
        names = self.book.list_recipe_names()
        
        self.assertEqual(len(names), 3)
        self.assertIn('Pasta', names)
        self.assertIn('Salad', names)
        self.assertIn('Bread', names)
    
    def test_remove_recipe(self):
        """Test removing a recipe."""
        self.book.add_recipe(self.sample_recipe)
        self.assertEqual(self.book.count_recipes(), 1)
        
        result = self.book.remove_recipe('Test Recipe')
        
        self.assertTrue(result)
        self.assertEqual(self.book.count_recipes(), 0)
        self.assertNotIn('Test Recipe', self.book)
    
    def test_remove_nonexistent_recipe(self):
        """Test that removing nonexistent recipe returns False."""
        result = self.book.remove_recipe('Nonexistent Recipe')
        self.assertFalse(result)
    
    def test_update_recipe(self):
        """Test updating an existing recipe."""
        self.book.add_recipe(self.sample_recipe)
        
        updated_recipe = {
            'name': 'Test Recipe',
            'ingredients': ['2 cups flour', '3 eggs', '1 cup milk'],  # Changed
            'directions': 'Updated directions.'
        }
        
        result = self.book.update_recipe('Test Recipe', updated_recipe)
        
        self.assertTrue(result)
        
        retrieved = self.book.get_recipe('Test Recipe')
        self.assertEqual(len(retrieved['ingredients']), 3)
        self.assertEqual(retrieved['ingredients'][0], '2 cups flour')
    
    def test_update_nonexistent_recipe(self):
        """Test that updating nonexistent recipe returns False."""
        updated_recipe = {
            'name': 'Nonexistent',
            'ingredients': ['stuff'],
            'directions': 'do stuff'
        }
        
        result = self.book.update_recipe('Nonexistent', updated_recipe)
        self.assertFalse(result)
    
    def test_search_recipes_by_name(self):
        """Test searching recipes by name."""
        recipes = [
            {'name': 'Chocolate Cake', 'ingredients': ['flour'], 'directions': 'bake'},
            {'name': 'Vanilla Cookies', 'ingredients': ['flour'], 'directions': 'bake'},
            {'name': 'Chocolate Chip Cookies', 'ingredients': ['flour'], 'directions': 'bake'}
        ]
        
        for recipe in recipes:
            self.book.add_recipe(recipe)
        
        results = self.book.search_recipes('chocolate')
        
        self.assertEqual(len(results), 2)
        names = [r['name'] for r in results]
        self.assertIn('Chocolate Cake', names)
        self.assertIn('Chocolate Chip Cookies', names)
    
    def test_search_recipes_by_ingredient(self):
        """Test searching recipes by ingredient."""
        recipes = [
            {'name': 'Pasta', 'ingredients': ['tomato paste', 'pasta'], 'directions': 'cook'},
            {'name': 'Salad', 'ingredients': ['lettuce', 'tomato'], 'directions': 'toss'},
            {'name': 'Bread', 'ingredients': ['flour', 'yeast'], 'directions': 'bake'}
        ]
        
        for recipe in recipes:
            self.book.add_recipe(recipe)
        
        results = self.book.search_recipes('tomato')
        
        self.assertEqual(len(results), 2)
        names = [r['name'] for r in results]
        self.assertIn('Pasta', names)
        self.assertIn('Salad', names)
    
    def test_clear_all(self):
        """Test clearing all recipes."""
        recipes = [
            {'name': 'Recipe 1', 'ingredients': ['a'], 'directions': 'do'},
            {'name': 'Recipe 2', 'ingredients': ['b'], 'directions': 'do'},
            {'name': 'Recipe 3', 'ingredients': ['c'], 'directions': 'do'}
        ]
        
        for recipe in recipes:
            self.book.add_recipe(recipe)
        
        self.assertEqual(self.book.count_recipes(), 3)
        
        self.book.clear_all()
        
        self.assertEqual(self.book.count_recipes(), 0)


class TestRecipeBookTags(unittest.TestCase):
    """Test tag functionality."""
    
    def setUp(self):
        """Create temporary recipe book with tagged recipes."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.close()
        self.book = RecipeBook(self.temp_file.name)
        
        # Add recipes with tags
        self.recipes = [
            {
                'name': 'Pasta Marinara',
                'ingredients': ['pasta', 'sauce'],
                'directions': 'Cook',
                'tags': ['dinner', 'italian', 'quick']
            },
            {
                'name': 'Chocolate Cake',
                'ingredients': ['flour', 'chocolate'],
                'directions': 'Bake',
                'tags': ['dessert', 'party']
            },
            {
                'name': 'Caesar Salad',
                'ingredients': ['lettuce', 'dressing'],
                'directions': 'Toss',
                'tags': ['salad', 'quick', 'side dish']
            }
        ]
        
        for recipe in self.recipes:
            self.book.add_recipe(recipe)
    
    def tearDown(self):
        """Clean up."""
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_recipe_with_tags_added(self):
        """Test that recipes with tags are added correctly."""
        pasta = self.book.get_recipe('Pasta Marinara')
        self.assertIn('tags', pasta)
        self.assertEqual(len(pasta['tags']), 3)
        self.assertIn('dinner', pasta['tags'])
    
    def test_recipe_without_tags_gets_empty_list(self):
        """Test that recipe without tags gets empty tag list."""
        recipe = {
            'name': 'No Tags Recipe',
            'ingredients': ['ingredient'],
            'directions': 'Do stuff'
            # No 'tags' field
        }
        
        self.book.add_recipe(recipe)
        retrieved = self.book.get_recipe('No Tags Recipe')
        
        self.assertIn('tags', retrieved)
        self.assertEqual(retrieved['tags'], [])
    
    def test_add_tag_to_recipe(self):
        """Test adding a tag to existing recipe."""
        result = self.book.add_tag_to_recipe('Pasta Marinara', 'vegetarian')
        
        self.assertTrue(result)
        
        pasta = self.book.get_recipe('Pasta Marinara')
        self.assertIn('vegetarian', pasta['tags'])
    
    def test_add_duplicate_tag_ignored(self):
        """Test that adding duplicate tag doesn't create duplicates."""
        # Add tag
        self.book.add_tag_to_recipe('Pasta Marinara', 'italian')
        
        # Verify only one instance
        pasta = self.book.get_recipe('Pasta Marinara')
        count = pasta['tags'].count('italian')
        self.assertEqual(count, 1)
    
    def test_add_tag_to_nonexistent_recipe(self):
        """Test that adding tag to nonexistent recipe returns False."""
        result = self.book.add_tag_to_recipe('Nonexistent', 'tag')
        self.assertFalse(result)
    
    def test_remove_tag_from_recipe(self):
        """Test removing a tag from recipe."""
        result = self.book.remove_tag_from_recipe('Pasta Marinara', 'quick')
        
        self.assertTrue(result)
        
        pasta = self.book.get_recipe('Pasta Marinara')
        self.assertNotIn('quick', pasta['tags'])
    
    def test_remove_nonexistent_tag(self):
        """Test removing tag that doesn't exist returns False."""
        result = self.book.remove_tag_from_recipe('Pasta Marinara', 'nonexistent-tag')
        self.assertFalse(result)
    
    def test_get_all_tags(self):
        """Test getting all unique tags."""
        all_tags = self.book.get_all_tags()
        
        # Should have 7 unique tags
        expected_tags = ['dessert', 'dinner', 'italian', 'party', 'quick', 'salad', 'side dish']
        self.assertEqual(all_tags, expected_tags)
    
    def test_get_tag_counts(self):
        """Test getting tag usage counts."""
        counts = self.book.get_tag_counts()
        
        self.assertEqual(counts['quick'], 2)  # Pasta and Salad
        self.assertEqual(counts['italian'], 1)  # Just Pasta
        self.assertEqual(counts['dessert'], 1)  # Just Cake
    
    def test_search_by_tag(self):
        """Test searching recipes by single tag."""
        quick_recipes = self.book.search_by_tag('quick')
        
        self.assertEqual(len(quick_recipes), 2)
        names = [r['name'] for r in quick_recipes]
        self.assertIn('Pasta Marinara', names)
        self.assertIn('Caesar Salad', names)
    
    def test_search_by_tag_case_insensitive(self):
        """Test that tag search is case-insensitive."""
        results1 = self.book.search_by_tag('QUICK')
        results2 = self.book.search_by_tag('quick')
        results3 = self.book.search_by_tag('QuIcK')
        
        self.assertEqual(len(results1), len(results2))
        self.assertEqual(len(results2), len(results3))
    
    def test_search_by_multiple_tags_any(self):
        """Test searching by multiple tags (match ANY)."""
        # Find recipes that are EITHER dessert OR italian
        results = self.book.search_by_multiple_tags(['dessert', 'italian'], match_all=False)
        
        self.assertEqual(len(results), 2)  # Pasta and Cake
        names = [r['name'] for r in results]
        self.assertIn('Pasta Marinara', names)
        self.assertIn('Chocolate Cake', names)
    
    def test_search_by_multiple_tags_all(self):
        """Test searching by multiple tags (match ALL)."""
        # Find recipes that are BOTH dinner AND quick
        results = self.book.search_by_multiple_tags(['dinner', 'quick'], match_all=True)
        
        self.assertEqual(len(results), 1)  # Just Pasta
        self.assertEqual(results[0]['name'], 'Pasta Marinara')
    
    def test_get_recipes_by_tag(self):
        """Test organizing recipes by tag (Chrome tab groups style)."""
        tag_groups = self.book.get_recipes_by_tag()
        
        # Check 'quick' tag
        self.assertIn('quick', tag_groups)
        self.assertEqual(len(tag_groups['quick']), 2)
        self.assertIn('Pasta Marinara', tag_groups['quick'])
        self.assertIn('Caesar Salad', tag_groups['quick'])
        
        # Check 'dessert' tag
        self.assertIn('dessert', tag_groups)
        self.assertEqual(len(tag_groups['dessert']), 1)
        self.assertIn('Chocolate Cake', tag_groups['dessert'])
    
    def test_tags_persist_across_sessions(self):
        """Test that tags are saved and loaded correctly."""
        # Add tag
        self.book.add_tag_to_recipe('Chocolate Cake', 'kid-friendly')
        
        # Create new session
        new_book = RecipeBook(self.temp_file.name)
        
        cake = new_book.get_recipe('Chocolate Cake')
        self.assertIn('kid-friendly', cake['tags'])


class TestRecipeBookPersistence(unittest.TestCase):
    """Test data persistence (save/load) functionality."""
    
    def setUp(self):
        """Create temporary file for testing."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up temporary file."""
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_save_and_load(self):
        """Test that recipes persist across sessions."""
        # Session 1: Add recipes
        book1 = RecipeBook(self.temp_file.name)
        
        recipes = [
            {'name': 'Recipe 1', 'ingredients': ['a'], 'directions': 'do a'},
            {'name': 'Recipe 2', 'ingredients': ['b'], 'directions': 'do b'}
        ]
        
        for recipe in recipes:
            book1.add_recipe(recipe)
        
        # Session 2: Load and verify (simulate program restart)
        book2 = RecipeBook(self.temp_file.name)
        
        self.assertEqual(book2.count_recipes(), 2)
        self.assertIn('Recipe 1', book2)
        self.assertIn('Recipe 2', book2)
    
    def test_remove_persists(self):
        """Test that removing recipe persists."""
        # Add recipes
        book1 = RecipeBook(self.temp_file.name)
        book1.add_recipe({'name': 'Recipe 1', 'ingredients': ['a'], 'directions': 'do'})
        book1.add_recipe({'name': 'Recipe 2', 'ingredients': ['b'], 'directions': 'do'})
        
        # Remove one
        book1.remove_recipe('Recipe 1')
        
        # Load new session
        book2 = RecipeBook(self.temp_file.name)
        
        self.assertEqual(book2.count_recipes(), 1)
        self.assertNotIn('Recipe 1', book2)
        self.assertIn('Recipe 2', book2)
    
    def test_handles_corrupted_file(self):
        """Test that corrupted file is handled gracefully."""
        # Write invalid JSON to file
        with open(self.temp_file.name, 'w') as f:
            f.write("not valid json {]")
        
        # Should not crash, should start fresh
        book = RecipeBook(self.temp_file.name)
        self.assertEqual(book.count_recipes(), 0)
    
    def test_handles_missing_file(self):
        """Test that missing file creates new empty book."""
        # Use non-existent file path
        nonexistent_path = Path(self.temp_file.name).parent / "nonexistent.json"
        
        book = RecipeBook(str(nonexistent_path))
        
        self.assertEqual(book.count_recipes(), 0)
        
        # Cleanup
        nonexistent_path.unlink(missing_ok=True)


class TestRecipeBookImportExport(unittest.TestCase):
    """Test import/export functionality."""
    
    def setUp(self):
        """Set up test files."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.close()
        
        self.export_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.export_file.close()
        
        self.book = RecipeBook(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test files."""
        Path(self.temp_file.name).unlink(missing_ok=True)
        Path(self.export_file.name).unlink(missing_ok=True)
    
    def test_export_to_json(self):
        """Test exporting recipe book to JSON."""
        recipes = [
            {'name': 'Recipe 1', 'ingredients': ['a'], 'directions': 'do a'},
            {'name': 'Recipe 2', 'ingredients': ['b'], 'directions': 'do b'}
        ]
        
        for recipe in recipes:
            self.book.add_recipe(recipe)
        
        # Export
        self.book.export_to_json(self.export_file.name)
        
        # Verify export file exists and has content
        self.assertTrue(Path(self.export_file.name).exists())
        
        with open(self.export_file.name, 'r') as f:
            exported_data = json.load(f)
        
        self.assertEqual(len(exported_data), 2)
    
    def test_import_from_json_replace(self):
        """Test importing recipes (replace mode)."""
        # Create export file with recipes
        import_recipes = [
            {'name': 'Imported 1', 'ingredients': ['x'], 'directions': 'do x'},
            {'name': 'Imported 2', 'ingredients': ['y'], 'directions': 'do y'}
        ]
        
        with open(self.export_file.name, 'w') as f:
            json.dump(import_recipes, f)
        
        # Add existing recipe to book
        self.book.add_recipe({'name': 'Existing', 'ingredients': ['z'], 'directions': 'do z'})
        
        # Import (replace mode)
        count = self.book.import_from_json(self.export_file.name, merge=False)
        
        self.assertEqual(count, 2)
        self.assertEqual(self.book.count_recipes(), 2)
        self.assertNotIn('Existing', self.book)
        self.assertIn('Imported 1', self.book)
    
    def test_import_from_json_merge(self):
        """Test importing recipes (merge mode)."""
        # Create export file with recipes
        import_recipes = [
            {'name': 'Imported 1', 'ingredients': ['x'], 'directions': 'do x'},
            {'name': 'Imported 2', 'ingredients': ['y'], 'directions': 'do y'}
        ]
        
        with open(self.export_file.name, 'w') as f:
            json.dump(import_recipes, f)
        
        # Add existing recipe to book
        self.book.add_recipe({'name': 'Existing', 'ingredients': ['z'], 'directions': 'do z'})
        
        # Import (merge mode)
        count = self.book.import_from_json(self.export_file.name, merge=True)
        
        self.assertEqual(count, 2)
        self.assertEqual(self.book.count_recipes(), 3)
        self.assertIn('Existing', self.book)
        self.assertIn('Imported 1', self.book)
    
    def test_import_skips_duplicates_in_merge(self):
        """Test that import in merge mode skips duplicates."""
        # Add recipe
        self.book.add_recipe({'name': 'Duplicate', 'ingredients': ['a'], 'directions': 'do'})
        
        # Create import file with same recipe
        import_recipes = [
            {'name': 'Duplicate', 'ingredients': ['a'], 'directions': 'do'},
            {'name': 'New Recipe', 'ingredients': ['b'], 'directions': 'do'}
        ]
        
        with open(self.export_file.name, 'w') as f:
            json.dump(import_recipes, f)
        
        # Import (merge)
        count = self.book.import_from_json(self.export_file.name, merge=True)
        
        # Should only import the non-duplicate
        self.assertEqual(count, 1)
        self.assertEqual(self.book.count_recipes(), 2)


class TestRecipeBookSpecialMethods(unittest.TestCase):
    """Test special methods (__len__, __contains__, __repr__)."""
    
    def setUp(self):
        """Create temporary recipe book."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.close()
        self.book = RecipeBook(self.temp_file.name)
    
    def tearDown(self):
        """Clean up."""
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_len(self):
        """Test __len__ method."""
        self.assertEqual(len(self.book), 0)
        
        self.book.add_recipe({'name': 'Recipe', 'ingredients': ['a'], 'directions': 'do'})
        self.assertEqual(len(self.book), 1)
    
    def test_contains(self):
        """Test __contains__ method (in operator)."""
        self.book.add_recipe({'name': 'Test Recipe', 'ingredients': ['a'], 'directions': 'do'})
        
        self.assertTrue('Test Recipe' in self.book)
        self.assertFalse('Nonexistent' in self.book)
    
    def test_repr(self):
        """Test __repr__ method."""
        repr_str = repr(self.book)
        
        self.assertIn('RecipeBook', repr_str)
        self.assertIn('recipes=0', repr_str)


if __name__ == '__main__':
    unittest.main(verbosity=2)